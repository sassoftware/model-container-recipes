#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import zipfile
import time
import json
import logging
from flask import Flask, jsonify, request, Response
from flask import send_from_directory

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def locate_zip_file(dest):
    # search for zip file
    for file1 in os.listdir(dest):
        if file1.endswith(".zip"):
            return file1
    return None


def unzip_file(zip_file, dest):
    # unzip
    zip_ref = zipfile.ZipFile(zip_file, 'r')

    if not os.path.isdir(dest):
        os.mkdir(dest)
    zip_ref.extractall(dest)
    zip_ref.close()


# find the first file which matches the pattern
def find_file(suffix):
    current_dir = os.getcwd()
    for file in os.listdir(current_dir):
        if file.endswith(suffix):
            filename = file
            return os.path.join(current_dir, filename)

    return None


def find_names_by_role(filename, role):
    var_file = find_file(filename)
    if var_file is None:
        return None
    if os.path.isfile(var_file):
        with open(var_file) as f:
            json_object = json.load(f)

        names = []
        for row in json_object:
            if row['role'] == role:
                names.append(row["name"])
        if names == []:
            return None
        return names
    else:
        app.logger.info('Didnot find any role: ' + role + ' in file: ' + filename)
        return None


def find_score_script(filename):
    return find_names_by_role(filename, 'score')


def find_models(filename):
    return find_names_by_role(filename, 'model')


# setup model repository directory
model_repo = '/pybox/model'
if "model_repository" in os.environ:
    model_repo = os.environ['model_repository']

app.logger.info("Model location: " + model_repo)
if not os.path.isdir(model_repo):
    raise RuntimeError("model repository not existed!")

# locate the zip file
model_zip_file_name = locate_zip_file(model_repo)
if model_zip_file_name is None:
    app.logger.info("Error: Can't find model zip file in the repository!")
    raise RuntimeError("Can't find model zip file in the repository!")

subfolder = model_repo

model_zip_file = os.path.join(model_repo, model_zip_file_name)

# extract the zip file
unzip_file(model_zip_file, subfolder)

print("Completed Initialization!")


# return test_id value
# the result file will be <test_id>.csv
def score(filename):
    app.logger.debug(filename)

    # based on current timestamp
    test_id = str(time.time())
    output_file = test_id + '.csv'
    log_file = test_id + '.log'
    app.logger.debug(output_file)

    # keep current dir
    current_dir = os.getcwd()
    os.chdir(subfolder)

    # search for score script
    # 1) search for ContainerWrapper.py
    if os.path.isfile("ContainerWrapper.py"):
        score_file = "ContainerWrapper.py"
    else:
        # 2) search for score code defined in fileMetadata.json
        names = find_score_script('fileMetadata.json')

        if names is None:
            # 3) find the first score script in the current then
            score_file = '_score.py'
            for file1 in os.listdir("."):
                if file1.endswith("score.py") and file1 != score_file:
                    score_file = file1
                    break
        else:
            score_file = names[0]

    # search for model
    names = find_models('fileMetadata.json')
    model_param = ''
    if names is not None:
        model_param = ' -m '+names[0]

    command_str = 'python -W ignore ' + score_file + model_param + ' -i ' + filename+' -o ' + output_file 

    f = open(log_file,"w+")
    f.write("Scoring...\n")
    f.write(" "+command_str+"\n")
    f.close()

    command_str = command_str + ' >> '+log_file + ' 2>&1'

    app.logger.info(command_str)
    os.system(command_str)

    f = open(log_file,"a")
    f.write("\nCompleted!\n")
    f.close()

    os.chdir(current_dir)

    return test_id


@app.route('/', methods=['GET'])
def ping():
    return return_text("pong")


@app.route('/executions', methods=['POST'])
def batch():
    """
 * Accept input data in csv file and store it to subdirectory <model repo dir>/<job definition id>
 * Try sample.csv if there's no input data file;
 * execute the python program (under the anaconda environment)
 * extract score filename from fileMetadata.json if any, otherwise assume the first python script ending with 'score.py'. Default script is _score.py
 * execution
   - cd <model repo dir>/<job definition id>
   - python score.py -i <inputdata.csv> -o <timestamp>.csv
 * return output filename with the path if succeed
 * TODO single score, async
    """
    try:
        file = request.files['file']
        # print(file)
        input_file_name = file.filename
        input_file = os.path.join(subfolder, input_file_name)
        file.save(input_file)
    except:
        input_file_name = 'sample.csv'
        input_file = os.path.join(subfolder, input_file_name)
        if not os.path.isfile(input_file):
            return bad_request("Can't find sample.csv in the model zip file!")

    test_id = score(input_file)
    return created_request(test_id)


# In future we could extend this call to two calls, one for checking status and the other for retrieving csv file
@app.route('/query/<test_id>', methods=['GET'])
def query(test_id):
    """
    read csv file from <test_id>.csv as an attachment
    """
    test_id = test_id.lower()
    if not test_id.endswith('.csv'):
        output_file = test_id + '.csv'
    else:
        output_file = test_id

    full_output_file = os.path.join(subfolder, output_file)
    if not os.path.isfile(full_output_file):
        return not_found(full_output_file)

    return send_from_directory(subfolder, output_file, as_attachment=True)


# return <test_id>.log
@app.route('/query/<test_id>/log', methods=['GET'])
def querylog(test_id):
    """
    read log file from <test_id>.log as an attachment
    """
    test_id = test_id.lower()
    output_file = test_id + '.log'

    full_output_file = os.path.join(subfolder, output_file)
    if not os.path.isfile(full_output_file):
        return not_found(full_output_file)

    return send_from_directory(subfolder, output_file, as_attachment=True)


# get gunicorn log
@app.route('/system/log', methods=['GET'])
def systemlog():

    full_log_file = "/var/log/gunicorn.log"
    if not os.path.isfile(full_log_file):
        return not_found(full_log_file)

    return send_from_directory('/var/log', 'gunicorn.log', as_attachment=True)


def return_text(text):
    return Response(text, status=200, mimetype='text/plain')


def created_request(msg=None):
    message = {
        'status': 201,
        'id': msg
    }
    resp = jsonify(message)
    resp.status_code = 201

    return resp


@app.errorhandler(400)
def bad_request(error=None):
    message = {
        'status': 400,
        'message': 'Bad Request: ' + request.url + '--> Please check your data payload...' + error,
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp


@app.errorhandler(404)
def not_found(filename=None):
    message = {
        'status': 404,
        'message': 'Bad Request: ' + request.url + '--> Please check your input...' + filename,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
