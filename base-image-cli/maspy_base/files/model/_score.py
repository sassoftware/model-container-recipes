#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import json
import logging
import os
import sys

import pandas as pd
import numpy as np
from sklearn.base import TransformerMixin
import maspy

__version__ = "1.0"


class DataFrameImputer(TransformerMixin):

    def __init__(self):
        """Impute missing values.

        Columns of dtype object are imputed with the most frequent value
        in column.

        Columns of other types are imputed with mean of column.

        """
    def fit(self, X, y=None):

        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].mean() for c in X],
            index=X.columns)

        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)


# find the first file which matches the pattern
def find_file(suffix):
    current_dir = os.path.dirname( os.path.abspath(__file__))
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
    names = find_names_by_role(filename, 'score')
    if names is not None:
        return names[0]
    else:
        return None


# try AstoreMetadata.json or dmcas_sha1key.json
def get_astore_key():
    # search key in AstoreMetadata.json
    meta_file = find_file("AstoreMetadata.json")
    if meta_file is None:
        # search in other file
        meta_file = find_file("_sha1key.json")
        if meta_file is not None:
            with open(meta_file) as f:
                dt = json.load(f)
            return str(dt['SASTableData+_ASTOREKEY'][0]["key"])
    else:
        with open(meta_file) as f:
            dt = json.load(f)
        return str(dt[0]["key"])
    return None


def has_astore():
    meta_file = find_file("AstoreMetadata.json")
    if meta_file is None:
        return False
    else:
        return True


# replace the package line if need
# such as "package &SCOREPACK/overwrite=yes;"
def fix_package_line(ds2_file):
    bad_token = "package &"
    s = open(ds2_file).read()
    if bad_token in s:
        print("Rewriting " + ds2_file)
        s = s.replace(bad_token, 'package ')
        f = open(ds2_file, 'w')
        f.write(s)
        f.close()


def find_pkg_score_script():
    pkg_file = find_file('.ds2')
    if pkg_file is None:
        pkg_file = find_file('packagescorecode.sas')
    if pkg_file is None:
        pkg_file = find_file('pkg_score.sas')
    return pkg_file


def run(input_file, output_file):

    is_astore_model = has_astore()
    # find ds2 score file
    ds2_file = find_score_script('fileMetadata.json')
    
    # user package score script for astore model
    if is_astore_model:
        pkg_score_file = find_pkg_score_script()
        if pkg_score_file is not None:
            ds2_file = pkg_score_file

    if ds2_file is None:
        print('ERROR : Can not find score code file')
        return {}

    mas = maspy.MASsf(cfgname='mascontainer')
    fix_package_line(ds2_file)

    if is_astore_model: 
        astore_file = find_file('.astore')
        print(astore_file)
        astore_key = get_astore_key()
        if astore_file is None:
            print('ERROR : Can not find astore file')
            return {}

        if astore_key is None:
            print('ERROR: can not find the astore_key')
            return {}

    comp = [{'name' : "ds2score", 'lang': 'ds2', 'file': ds2_file}]
    if is_astore_model:
        comp.append({'name': "myastore", 'lang': 'astore', 'file': astore_file, 'sha1': astore_key})

    print(ds2_file)

    print('publishing...')
    ret = mas.publishComposite("ds2score", "score", comp)
    if 'publishing apparently failed' in ret:
        print('publish failed:', ret)
        return {}

    data1 = pd.read_csv(input_file)
    data = DataFrameImputer().fit_transform(data1)

    inputvar_file = find_file('inputVar.json')
    if inputvar_file is not None and os.path.isfile(inputvar_file):
        print('re-order input data')
        # order input data
    
        with open(inputvar_file) as f:
            dt = json.load(f)

        names = []
        for row in dt:
            names.append(row["name"])

        # print(names)
        df2 = data[names]
    else:
        print("same order as input file since there's no inputVar.json")
        df2 = data

    print('executing...')
    out = mas.execute("ds2score", "score", df2)

    if out is None:
        return dict(
            FAIL=dict(
                msg="Scoring dataframe failed",
                df=df2.to_dict()))

    print('printing first few lines...')
    print(out.head())
    out.to_csv(output_file,sep=',',index=False)
    return out.to_dict()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Score')
    parser.add_argument('-i', dest="scoreInputCSV", required=True, help='input filename')
    parser.add_argument('-o', dest="scoreOutputCSV", required=True, help='output csv filename')

    args = parser.parse_args()
    input_file = args.scoreInputCSV
    output_file = args.scoreOutputCSV

    if not os.path.isfile(input_file):
        print('Not found input file',input_file)
        sys.exit()
            
    result = run(input_file, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
