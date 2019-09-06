#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import configparser
import os
import shutil
import zipfile
import datetime
import time
import docker
# make sure it is python-slugify
from slugify import slugify
from collections import OrderedDict
from CloudAWSLib import CloudAWSLib
from CloudAzureLib import CloudAzureLib
from CloudGCPLib import CloudGCPLib
from K8sLib import K8sLib
import traceback
import json
import fileinput
import requests
import mmAuthorization

# Constants
CONTAINER_PORT = 8080
HOST_PORT = 8080


class ModelImageLib(object):
    def __init__(self):
        self.docker_client = docker.from_env()
        # initial cloud libraries
        self.mm_docker_aws = None
        self.mm_docker_gcp = None
        self.mm_docker_azure = None
        self.k8s = None

        # init class variables
        self.verbose_on = False
        self.model_repo_host = None
        self.base_repo = None
        self.verbose_on = None
        self.provider  = "Dev"
        self.kubernetes_context = None
        self.cur_path = os.path.dirname(__file__)
        self.logs_folder = os.path.join(self.cur_path, "logs")
        if not os.path.isdir(self.logs_folder):
            os.mkdir(self.logs_folder)
        self.log_file_full_path = os.path.join(self.logs_folder, "cli.log")

    # load configuration from file
    # if provider value is passed in, it will overwrite the setting in config.properties
    # return False if failed
    def init_config(self, p=None):
        print("Loading configuration properties...")

        try:
            config = configparser.RawConfigParser()
            config.read('config.properties')

            self.model_repo_host = ModelImageLib.read_config_option(config, 'Config', 'model.repo.host')
            if self.model_repo_host is None or len(self.model_repo_host) < 1:
                print("Please set Model Repository access URL in model.repo.host field inside config.properties file!")
                return False

            verbose_str = ModelImageLib.read_config_option(config, 'Config', 'verbose')
            if verbose_str is not None and verbose_str == 'True':
                self.verbose_on = True
            else:
                self.verbose_on = False

            if p is not None:
                self.provider = p
            else:
                self.provider = ModelImageLib.read_config_option(config, 'Config', 'provider.type')

            self.kubernetes_context = ModelImageLib.read_config_option(config, self.provider, 'kubernetes.context')

            registry = None
            if self.provider == 'AWS':
                # login amazon ecr
                self.mm_docker_aws = CloudAWSLib(config, self.docker_client)
                registry = self.mm_docker_aws.login()

            elif self.provider == 'GCP':
                # login Google Container Registry
                self.mm_docker_gcp = CloudGCPLib(config, self.docker_client)
                registry = self.mm_docker_gcp.login()

            elif self.provider == 'Azure':
                # login Azure Container Registry
                self.mm_docker_azure = CloudAzureLib(config, self.docker_client)
                registry = self.mm_docker_azure.login()
            else:
                registry = ModelImageLib.read_config_option(config, self.provider, 'base.repo')

            if registry is None:
                return False

            self.convert_base_repo(registry)

            # TODO only initialize k8s for certain actions
            if self.kubernetes_context is not None and len(self.kubernetes_context) > 0:
                print("Initializing kubernetes configuration...", self.kubernetes_context)
                self.k8s = K8sLib(self.provider, self.kubernetes_context, self.verbose_on)
        except:
            print("Error loading configuration from config.properties file! Double-check Docker daemon or other environment.")
            print(traceback.format_exc())
            return False

        print('  verbose:', self.verbose_on)
        print('  model.repo.host:', self.model_repo_host)
        print('  provider.type:', self.provider)
        print('  base.repo:', self.base_repo)
        print('  kubernetes.context:', self.kubernetes_context)

        print("===================================")
        return True

    # log timestamp, command, arguments, results
    def log(self, *args):
        current_time = str(datetime.datetime.now())
        with open(self.log_file_full_path, 'a', encoding='utf-8') as f:
            f.write(current_time+',' + ','.join(args)+'\n')

    # list model by partial key
    def listmodel(self, key=None):
        self.print_msg("Getting model list...")
        try:
            mm_auth = mmAuthorization.mmAuthorization("myAuth")
            auth_token = mm_auth.get_auth_token(self.model_repo_host)
            headers = {
                mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + auth_token
            }
        except:
            print(traceback.format_exc())
            raise RuntimeError("ERROR! Failed to auth token")

        models_url = self.model_repo_host + "/modelRepository/models?limit=999&start=0"
        try:
            response = requests.get(models_url, headers=headers)
            jsondata = response.json()
            models = jsondata['items']
            if len(models) > 0:
                for model in models:
                    # print(model)
                    model_name = model['name']
                    model_name = model_name.lower()
                    model_id = model['id']
                    model_version = model['modelVersionName']
                    if key is not None:
                        key = key.lower()
                    # ignore if there's partial key and the model name doesn't have the key (case insensitive)
                    if key is not None and key != 'all' and key not in model_name:
                        continue
                    print("Model name", model_name)
                    print("Model UUID", model_id)
                    print("Model version", model_version)
                    if 'projectName' in model.keys() and model['projectName'] is not None:
                        print("Project name", model['projectName'])
                    if 'scoreCodeType' in model.keys():
                        print("Score Code Type", model['scoreCodeType'])
                    else:
                        print('Warning! No score code type defined!')
                    model_name = slugify(model_name)
                    # use the first 8 characters of model_name
                    tag_name = model_name[:8] + '_' + model_id
                    repo = self.base_repo + tag_name + ":latest"
                    # TODO compare the model version with the image version
                    print("Image URL (not verified):", repo)
                    print("==========================")
            self.print_msg("Guides: > python model_image_generation.py publish id <uuid>")
            self.print_msg("Guides: > python model_image_generation.py launch <image url>")
            self.print_msg("Guides: > python model_image_generation.py score <image url> <input file>")
        except:
            print(traceback.format_exc())
            raise RuntimeError("ERROR! Failed to get model list")

    #
    # copy astore file if it is an astore model
    # trigger astore generation command if astore file is not available in the directory
    #
    def copy_astore(self, subfolder, zip_file, model_id):
        astore_folder = "/opt/sas/viya/config/data/modelsvr/astore/"

        f = zipfile.ZipFile(zip_file, "r")
        astore_file_name = self.get_astore_name(f)
        f.close()
        if astore_file_name is None:
            return

        print("Copying astore file from directory", astore_folder)
        full_astore_path = astore_folder + astore_file_name + ".astore"
        self.print_msg(full_astore_path)
        if not os.path.isfile(full_astore_path):
            # make sure to trigger command
            print("Making REST API call to generate astore file...")
            self.download_model_astore(model_id, astore_file_name)

            # wait for up to 60s for finishing
            done = False
            past = 0
            while not done:
                if os.path.isfile(full_astore_path):
                    done = True
                else:
                    time.sleep(5) # 5s
                    past = past + 5
                    if past > 60:
                        break

            if not done:
                print("Error: Could not get astore file!")
                exit(1)

        self.print_msg(subfolder)
        shutil.copy(full_astore_path, subfolder)
        os.chmod(os.path.join(subfolder, astore_file_name + ".astore"), 0o777)

    #
    # API call to copy an astore for a model to the location
    # /config/data/modelsvr/astore
    #
    def download_model_astore(self, model_id, astore_name):
        try:
            mm_auth = mmAuthorization.mmAuthorization("myAuth")
            auth_token = mm_auth.get_auth_token(self.model_repo_host)
            headers = {
                "Accept": "application/vnd.sas.model.analytic.store+json",
                mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + auth_token
            }
        except:
            raise RuntimeError("ERROR! Failed to auth token")

        request_url = self.model_repo_host + f"/modelRepository/models/{model_id}/analyticStore/{astore_name}"

        try:
            r = requests.put(request_url, headers=headers)
            # print(r.status_code)
            if r.status_code != 202:
                raise RuntimeError("ERROR! Failed to generate astore file")

        except:
            raise RuntimeError("ERROR! Failed to generate astore file")

        return

    ##########
    # prepare the dependency lines from requirements.json
    # and append them before ENTRYPOINT in Dockerfile
    def add_dep_lines(self, subfolder):
        # search for special requirements.json file
        requirements_with_full_path = os.path.join(subfolder, 'requirements.json')
        if not os.path.isfile(requirements_with_full_path):
            return
        print("Installing dependencies defined from requirements.json...")
        dep_lines = ''
        with open(requirements_with_full_path) as f:
            json_object = json.load(f, object_pairs_hook=OrderedDict)
            for row in json_object:
                step = row['step']
                command = row['command']
                dep_lines = dep_lines + '#'+step+'\n'
                dep_lines = dep_lines + 'RUN '+command+'\n'
        dockerfile_path = os.path.join(subfolder, 'Dockerfile')
        self.print_msg('Inserting dependency lines in Dockerfile')
        self.print_msg(dep_lines)
        for line in fileinput.FileInput(dockerfile_path, inplace=1):
            if line.startswith("ENTRYPOINT"):
                line = line.replace(line, dep_lines+line)
            print(line, end='')

    # unzip the requirements.json from model zip file if available
    # examine the requirements.json and include the command lines into Dockerfile in the same subfolder
    def handle_dependencies(self, subfolder, zip_file):
        f = zipfile.ZipFile(zip_file, "r")
        req_file_name = self.extract_req_file(f, subfolder)
        f.close()
        if req_file_name is None:
            return
        self.add_dep_lines(subfolder)

    #  push the image to remote repo
    def push_to_repo(self, my_image, tag_name, version_id):
        repo = self.base_repo + tag_name

        self.print_msg("Docker repository URL: ", self.base_repo)

        # default is latest, always using latest
        remote_version_tag = repo + ':' + version_id
        remote_version_latest = repo + ':latest'

        self.print_msg(remote_version_tag)
        if my_image.tag(repo, version_id) is False:
            raise RuntimeError("failed on tagging")

        if my_image.tag(repo, "latest") is False:
            raise RuntimeError("failed on tagging remote latest")

        print("Creating repo...")
        if self.provider == 'AWS':
            if not self.mm_docker_aws.create_ecr_repo(tag_name):
                raise RuntimeError("Failed on creating ecr repo")

        print("Pushing to repo...")

        client = self.docker_client
        ret_str = client.images.push(remote_version_tag)
        if 'errorDetail' in ret_str:
            print("Error: ", ret_str)
            raise RuntimeError("Failed on push")

        ret_str = client.images.push(remote_version_latest)
        if 'errorDetail' in ret_str:
            print("Error: ", ret_str)
            raise RuntimeError("Failed on push")

        print("Model image URL:", remote_version_latest)
        return remote_version_latest

    # return True if good
    def url_ok(self, image_url):
        print("Validating image repository url...")
        client = self.docker_client

        try:
            if self.provider == 'AWS':
                auth_config = self.mm_docker_aws.get_auth_config_payload()
                client.images.pull(image_url, auth_config=auth_config)
            else:
                client.images.pull(image_url)
        except Exception as e:
            print("Failed on validating", image_url)
            print(traceback.format_exc())
            return False
        print("Completed validation.")
        return True

    def download_model_content(self, model_id):
        print("Downloading model", model_id, "from model repository...")

        # images folder under the current directory
        data_path = os.path.join(self.cur_path, 'images')
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self.print_msg("Images folder:", data_path)

        filename = "model-"+model_id+".zip"
        # remove extension
        dirname = os.path.splitext(filename)[0]
        # must be lowercase
        dirname = dirname.lower()

        subfolder = os.path.join(data_path, dirname)
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        model_file_full_path = os.path.join(subfolder, filename)

        try:
            mm_auth = mmAuthorization.mmAuthorization("myAuth")
            auth_token = mm_auth.get_auth_token(self.model_repo_host)
            headers = {
                mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + auth_token
            }
        except:
            raise RuntimeError("ERROR! Failed to auth token")

        model_url = self.model_repo_host + "/modelRepository/models/"+model_id
        try:
            # http://<host>/modelRepository/models/d00bb4e3-0672-4e9a-a877-39249d2a98ab?format=zip
            result_url = model_url+"?format=zip"
            r = requests.get(result_url, allow_redirects=True, headers=headers)
            # print(r.status_code)
            if r.status_code == 404:
                raise RuntimeError("ERROR! Failed to get model file")

            open(model_file_full_path, 'wb').write(r.content)
            self.print_msg("Model zip file has been downloaded at", model_file_full_path)
        except:
            raise RuntimeError("ERROR! Failed to get model file")

        # copy astore file if it is an astore model
        self.copy_astore(subfolder, model_file_full_path, model_id)

        model_name, version_id, code_type = self.retrieve_model_info(model_url, headers)
        return model_file_full_path, model_name, version_id, code_type

    # copy specified model zip file to dest folder and return model info
    def get_model_info_from_file(self, model_file_in):
        if not os.path.exists(model_file_in):
            raise RuntimeError("ERROR! File not exists: " + model_file_in)
        try:
            # open zip file
            z = zipfile.ZipFile(model_file_in, "r")
            properties_bytes = z.read('ModelProperties.json')
            properties_str = properties_bytes.decode('utf-8')
            z.close()

            # parse from ModelProperties.json
            json_object = json.loads(properties_str)
            model_id = json_object['id']
            model_name = json_object['name']
            code_type = json_object['scoreCodeType']

            # images folder under the current directory
            data_path = os.path.join(self.cur_path, 'images')
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            self.print_msg("Images folder:", data_path)

            # remove extension
            model_file = os.path.basename(model_file_in)
            dirname = os.path.splitext(model_file)[0]
            # must be lowercase
            dirname = dirname.lower()

            subfolder = os.path.join(data_path, dirname)
            if not os.path.exists(subfolder):
                os.makedirs(subfolder)

            # copy zip file to destination folder
            shutil.copy(model_file_in, subfolder)
            model_file_full_path = os.path.join(subfolder, model_file)
            return model_file_full_path, model_id, model_name, None, code_type
        except:
            raise RuntimeError("Unable to read model information from specified file")

    # Publish model by model_id or model filename
    def publish(self, type, id_or_filename):
        """
     * If type is 'id', model_id is given,
     *    Retrieve model zip file from model repository, such as modelxxxxxx.zip
     *    Get astore by scp temporarily until the other method is ready to pull astore file from the SAS server
     * Otherwise no REST call,
     *    Get model_id, model_name, score_code_type from file  ModelProperties.json (no version information so far)
     *    We also assume astore is already included in the zip file
     *
     * create subfolder <tag>, and store zip file and template files in subfolder
     * return image url if succeed
        """

        if type == 'id':
            is_id = True
        else:
            is_id = False

        model_id = None
        model_file = None

        if is_id:
            model_id = id_or_filename
        else:
            model_file = id_or_filename

        if is_id:
            model_file_full_path, model_name, version_id, code_type = self.download_model_content(model_id)
        else:
            # get model_name, version_id, code_type from file
            model_file_full_path, model_id, model_name, version_id, code_type = self.get_model_info_from_file(model_file)
            if version_id is None:
                version_id = 'na'  # ModelProperties.json doesn't contain model version!
            if model_id is None:
                raise RuntimeError('Unable to retrieve model uuid!')

        self.print_msg(model_id, model_name, version_id, code_type)

        dest_folder = os.path.dirname(model_file_full_path)

        # verify meta data
        if model_name is None:
            raise RuntimeError('Unable to retrieve model name!')

        # Normalize the name
        model_name = slugify(model_name)
        self.print_msg("The name has been normalized to", model_name)

        # copy template to dest_folder
        if code_type == 'python' or code_type == 'Python':
            template_folder_name = 'template-py'  # pyml-base
        elif code_type == 'R' or code_type == 'r':
            template_folder_name = 'template-r'  # r-base
        else:  # default
            template_folder_name = 'template'  # maspy-base

        template_folder = os.path.join(self.cur_path, template_folder_name)
        if not os.path.exists(template_folder):
            raise RuntimeError("Template folder not existed!")

        dockerfile = os.path.join(template_folder, 'Dockerfile')
        # make sure that one of files is named after Dockerfile
        if not os.path.isfile(dockerfile):
            raise RuntimeError("There's no Dockerfile under template folder")

        self.print_msg("Template folder:", template_folder)

        # copy template files into subfolder
        src_files = os.listdir(template_folder)
        for file_name in src_files:
            full_file_name = os.path.join(template_folder, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest_folder)

        # read requirements.json from zip file if available
        # and include the dependency lines in Dockerfile
        self.handle_dependencies(dest_folder, model_file_full_path)

        # tag names
        # use the first 8 characters of model_name
        tagname = model_name[:8] + '_' + model_id
        local_tag = tagname + ':' + version_id
        local_tag_latest = tagname + ':latest'

        # build local image with docker daemon
        client = self.docker_client

        print("Building image...")
        self.print_msg(local_tag)
        myimage, _ = client.images.build(path=dest_folder, tag=local_tag, buildargs={"base_repo":self.base_repo}, nocache=True)
        # tag it as latest version too
        self.print_msg(local_tag_latest)
        # myimage.tag(local_tag_latest)
        myimage.tag(tagname, "latest")

        self.print_msg("Tag the image into a repository", myimage.short_id)
        remote_version_latest = self.push_to_repo(myimage, tagname, version_id)

        self.print_msg("==========================")
        self.print_msg("Guides: > python model_image_generation.py launch", remote_version_latest)
        self.print_msg("Guides: > python model_image_generation.py score", remote_version_latest, "<input file>")
        self.log('publish', model_id, version_id, remote_version_latest)
        return remote_version_latest

    # submit request to kubernetes to start a pod instance
    # return deployment_name and service url
    def launch(self, image_url):
        if not self.url_ok(image_url):
            return

        print("Launching container instance...")
        self.print_msg(image_url)

        # get tag name from the model_name
        tag_name = image_url.rsplit('/', 1)[-1]
        tag_name = tag_name.rsplit('_', 1)[0]
        tag_name = slugify(tag_name)
        # make sure it is not more than 64 characters
        tag_name = tag_name[:64]
        self.print_msg(tag_name)
        deployment_name, service_url = self.k8s.deploy_application(tag_name, image_url, HOST_PORT, CONTAINER_PORT)
        self.print_msg("==========================")
        if service_url is None:
            print("Deployment failed! Please check environment settings!")
            self.stop(deployment_name)

        self.log('launch', image_url, deployment_name, service_url)
        ModelImageLib.wait_for_service_up(service_url)
        if self.k8s.check_pod_status(deployment_name):
            self.print_msg("Guides: > python model_image_generation.py execute ", service_url, "<input file>")
            self.print_msg("Guides: > python model_image_generation.py stop", deployment_name)
            return deployment_name, service_url
        else:
            print("Deployment failed! Please check docker image url!")
            self.stop(deployment_name)

    # perform scoring in container instance with the input data file
    def execute(self, service_url, csv_file):
        print("Performing scoring in the container instance...")
        self.print_msg("service_url:", service_url)
        self.print_msg("csv_file:", csv_file)
        if not os.path.isfile(csv_file):
            raise RuntimeError('Error! Test data file doesn\'t exist!')

        if not service_url.endswith('/'):
            service_url = service_url + '/'
        execution_url = service_url + 'executions'
        headers = {
           'Accept': 'application/json'
           # don't send Content-type header by self
           # 'Content-Type': 'multipart/form-data'
        }
        file_name = os.path.basename(csv_file)
        files = {
            'file': (file_name, open(csv_file, 'rb'), 'application/octet-stream')
            }

        # r = requests.post(url, files=files, data=data, headers=headers)
        response = requests.post(execution_url, files=files, headers=headers)

        resp_json = response.json()

        if response.status_code != 201:
            self.print_msg(response.content)
            raise RuntimeError('Error! Failed to perform score execution!'+resp_json)

        self.print_msg(resp_json)
        test_id = resp_json['id']
        print('The test_id from score execution:', test_id)
        self.print_msg("==========================")
        self.print_msg("Guides: > python model_image_generation.py query", service_url, test_id)
        dest_file = os.path.join(self.logs_folder, test_id + '_input.csv')
        shutil.copy(csv_file, dest_file)
        self.log('execute', service_url, dest_file, test_id)
        return test_id

    # Retrieve the result from container instance
    def query(self, service_url, test_id):
        self.print_msg("service_url:", service_url)
        self.print_msg("test_id:", test_id)

        if not service_url.endswith('/'):
            service_url = service_url + '/'

        result_file = test_id + '.csv'
        result_url = service_url + 'query/'+result_file

        r = requests.get(result_url, allow_redirects=True)
        if r.status_code == 404:
            print("The test result is not available in the container instance.")
            print("Please retrieve and inspect the execution log or system log.")
            return None
        open(result_file, 'wb').write(r.content)
        print("The test result has been retrieved and written into file", result_file)

        print("Showing the first 5 lines")
        print("=========================")
        with open(result_file) as myfile:
            max = 5
            for line in myfile:
                max = max-1
                print(line.strip())
                if max < 1:
                    break

        self.print_msg("==========================")
        self.print_msg("Guides: 1) remember to stop instance after usage. You can find the deployment name by running")
        self.print_msg("    > kubectl get deployment")
        self.print_msg("Then execute: > python model_image_generation.py stop <deployment_name>")
        self.print_msg("Guides: 2) if result file includes error message, you could find the pod name and debug inside the instance as below")
        self.print_msg("    > kubectl get pod")
        self.print_msg("    > kubectl exec -it <pod name> -- /bin/bash")
        shutil.move(result_file, os.path.join(self.logs_folder, result_file))
        self.log('query', service_url, test_id, result_file)
        return result_file

    # Retrieve the execution logs from container instance
    def scorelog(self, service_url, test_id):
        self.print_msg("service_url:", service_url)
        self.print_msg("test_id:", test_id)

        if not service_url.endswith('/'):
            service_url = service_url + '/'

        result_file = test_id + '.log'
        result_url = service_url + 'query/'+test_id + '/log'

        r = requests.get(result_url, allow_redirects=True)
        if r.status_code == 404:
            print("The execution log is not available in the container instance.")
            return None
        open(result_file, 'wb').write(r.content)
        print("The execution log has been retrieved and written into file", result_file)

        print("Showing the first 5 lines")
        print("=========================")
        with open(result_file) as myfile:
            max = 5
            for line in myfile:
                max = max-1
                print(line.strip())
                if max < 1:
                    break

        self.print_msg("==========================")
        self.print_msg("Guides: 1) remember to stop instance after usage. You can find the deployment name by running")
        self.print_msg("    > kubectl get deployment")
        self.print_msg("Then execute: > python model_image_generation.py stop <deployment_name>")
        self.print_msg("Guides: 2) if result file includes error message, you could find the pod name and debug inside the instance as below")
        self.print_msg("    > kubectl get pod")
        self.print_msg("    > kubectl exec -it <pod name> -- /bin/bash")
        shutil.move(result_file, os.path.join(self.logs_folder, result_file))
        self.log('scorelog', service_url, test_id, result_file)
        return result_file

    # retrieve the system log from container instance
    def systemlog(self, service_url):
        self.print_msg("Retrieving systemlog from container...")
        self.print_msg("service_url:", service_url)

        if not service_url.endswith('/'):
            service_url = service_url + '/'

        result_url = service_url + 'system/log'
        systemlog_file = 'gunicorn.log'

        r = requests.get(result_url, allow_redirects=True)
        # just override
        open(systemlog_file, 'wb').write(r.content)
        print("The system log has been retrieved and written into file", systemlog_file)

        print("Displaying the last 5 lines")
        ModelImageLib.display_last_lines(systemlog_file, 5)
        return systemlog_file

    # terminate the deployment
    def stop(self, deployment_name):
        """
     * Accept name=<deployment_name>
     * submit request to kubernetes to stop a pod instance and delete the deployment
        """
        if deployment_name is None:
            raise RuntimeError('Error! Deployment name is empty!')

        self.print_msg(deployment_name)

        if self.k8s.delete_application(deployment_name):
            self.log('stop', deployment_name)
            print('Deletion succeeded')
        else:
            raise RuntimeError('Deletion failed')

    # Run the commands (launch, execute, query, stop) in batch
    def score(self, image_url, csv_file):
        deployment_name, service_url = self.launch(image_url)
        print("===============================")
        test_id = self.execute(service_url, csv_file)
        print("===============================")
        self.query(service_url, test_id)
        print("===============================")
        self.stop(deployment_name)

    # set verbose mode
    def set_verbose(self, b):
        print("Verbose:", b)
        self.verbose_on = b

    # print debug message when verbose is on
    def print_msg(self, *args):
        if self.verbose_on:
            print(*args)

    def convert_base_repo(self, registry):
        # remove https or http prefix
        registry = registry.lower()
        if 'http://' in registry:
            repo = registry[7:]
        elif 'https://' in registry:
            repo = registry[8:]
        else:
            repo = registry
        if not repo.endswith('/'):
            repo = repo + '/'

        self.base_repo = repo
        return repo

    ########## Static methods ###############
    @staticmethod
    def read_config_option(config, category, key):
        if config.has_option(category, key):
            s = config.get(category, key);
            return s.strip()
        else:
            return None

    @staticmethod
    def display_last_lines(file_name, number=None):
        with open(file_name, "r", encoding='utf-8') as f:
            all_logs = list(f)
            count = 0
            for line in reversed(all_logs):
                if number == 'all' or number is None or count < int(number):
                    print(line)
                count = count+1

    # wait for service up
    @staticmethod
    def wait_for_service_up(service_url):
        num = 0
        while num < 10:
            num = num + 1
            print('Checking whether the instance is up or not...')
            # timeout is 1 second
            try:
                r = requests.get(service_url, timeout=30)
                if r.status_code == 200 and r.text == 'pong':
                    print('Instance is up!')
                    return True
            except:
                print(num, '==Sleep 10 seconds...')
                time.sleep(10)

    # retrieve model information by REST call
    @staticmethod
    def retrieve_model_info(model_url, headers):
        try:
            response = requests.get(model_url, allow_redirects=True, headers=headers)
            # jsondata = json.loads(response.text)
            jsondata = response.json()
            model_name = jsondata['name']
            model_version_id = jsondata['modelVersionName']
            code_type = jsondata['scoreCodeType']

            return model_name, model_version_id, code_type
        except:
            print(traceback.format_exc())
            raise RuntimeError("ERROR! Failed to get model info")

    # check whether AstoreMetadata.json inside or not
    @staticmethod
    def is_astore_model(z):
        return ModelImageLib.include_file(z, 'AstoreMetadata.json')

    # extract requirement file from zipfile
    @staticmethod
    def extract_req_file(z, subfolder):
        return ModelImageLib.extract_file(z, subfolder, 'requirements.json')

    # get astore name which begins with _
    @staticmethod
    def get_astore_name(z):
        if ModelImageLib.is_astore_model(z):
            for x in z.namelist():
                if x.startswith("_"):
                    return x
        return None

    # check whether the file is in the root of the zip file
    @staticmethod
    def include_file(z, filename):
        for x in z.namelist():
            if x == filename:
                return True
        return False

    # unzip specified file from the zip file to the specified folder
    @staticmethod
    def extract_file(z, subfolder, filename):
        for x in z.namelist():
            if x == filename:
                z.extract(filename, subfolder)
                return x
        return None
