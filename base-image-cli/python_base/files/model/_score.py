#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#


# Default python score code which helps score Python model with pickle file.
# You have to write own score file if your Python model doesn't have pickle file.

# If the pickle file has not specified in command line arguments, the script
# will look for the first pickle file in the current directory and it quits if not found.

# The score script will read the input variables from inputVar.json, the output variables
# from outputVar.json.

# The score script reads the input data from input csv file and store the output data in csv file.

import argparse
import os
import os.path
import sys
import pandas as pd
import numpy as np
import pickle
import json
from sklearn.base import TransformerMixin

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


def load_var_names(filename):
    var_file = find_file(filename)
    if var_file is None:
        return None
    if os.path.isfile(var_file):
        with open(var_file) as f:
            json_object = json.load(f)

        names = []
        for row in json_object:
            names.append(row["name"])
        return names
    else:
        print('Didnot find file: ', filename)
        return None


def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3


def load_data_by_input_vars(data):
    names = load_var_names('inputVar.json')
    if names is None:
        return data
    else:
        newcolumns = intersection(list(data.columns), names)
        return data[newcolumns]

    
def run(model_file, input_file, output_file):
    if model_file is None:
        print('Not found Python pickle file!')
        sys.exit()
        
    if not os.path.isfile(input_file):
        print('Not found input file', input_file)
        sys.exit()
        
    inputDf = pd.read_csv(input_file).fillna(0)

    output_vars = load_var_names('outputVar.json')
    
    in_dataf = load_data_by_input_vars(inputDf)

    model = open(model_file, 'rb')
    pkl_model = pickle.load(model)
    model.close()

    tmpDf = DataFrameImputer().fit_transform(in_dataf)
    outputDf = pd.DataFrame(pkl_model.predict_proba(tmpDf))

    if output_vars is None:
        outputcols = map(lambda x: 'P_' + str(x), list(pkl_model.classes_))
    else:
        outputcols = map(lambda x: output_vars[x], list(pkl_model.classes_))
    outputDf.columns = outputcols

    # merge with input data
    outputDf = pd.merge(inputDf, outputDf, how='inner', left_index=True, right_index=True)

    print('printing first few lines...')
    print(outputDf.head())
    outputDf.to_csv(output_file, sep=',', index=False)
    return outputDf.to_dict()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Score')
    parser.add_argument('-m', dest="modelFile", help='model filename, default will be the first pkl file found in the directory')
    parser.add_argument('-i', dest="scoreInputCSV", required=True, help='input filename')
    parser.add_argument('-o', dest="scoreOutputCSV", required=True, help='output csv filename')

    args = parser.parse_args()
    model_file = args.modelFile
    input_file = args.scoreInputCSV
    output_file = args.scoreOutputCSV

    # search for the first pkl file in the directory if argument is not given
    if model_file is None:
        for file in os.listdir("."):
            if file.endswith(".pkl"):
                model_file = file
                break
            
    result = run(model_file, input_file, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
