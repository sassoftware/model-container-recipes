#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#


__version__ = '1.0'


import os
from shutil import copyfile

base_dir = os.path.dirname(os.path.realpath(__file__))


#
# copy file from source folder to destination folder
#
def copy_files(file_name, src_path, dest_path):
    src_file = os.path.join(src_path, file_name)
    if os.path.isfile(src_file):
        dest_file = os.path.join(dest_path, file_name)
        # print("Copying", src_file, "to", dest_file)
        copyfile(src_file, dest_file)
        return True
    return False


#
# build MAS dependency libraries from Viya installation directory
#
def prepare_mas_libs(viya_install_dir):
    print("Gathering MAS dependency libraries...")
    list_filename = os.path.join(base_dir, "tklibs.list")

    # maspy
    bin_path = os.path.join(viya_install_dir, "home/SASFoundation/utilities/bin")
    # tk libraries
    lib_path = os.path.join(viya_install_dir, "home/SASFoundation/sasexe")
    dest_lib_folder = os.path.join(base_dir, "files/libs")

    # four python scripts
    py_path = os.path.join(viya_install_dir, "home/SASFoundation/misc/embscoreeng")
    py_path2 = os.path.join(viya_install_dir, "home/SASFoundation/misc/embscoreeng/maspy")
    dest_py_folder = os.path.join(base_dir, "files/model/maspy")

    # Collect the maspy binary, maspy python scripts and tk libraries from viya installation
    # Check Viya installation directory
    if not os.path.isdir(lib_path) or not os.path.isdir(py_path):
        print("Error: wrong Viya installation directory. Please double-check the installation!")
        return False

    if not os.path.isdir(dest_lib_folder):
        os.mkdir(dest_lib_folder)

    if not os.path.isfile(list_filename):
        print("Error: could not find file", list_filename)
        return False

    if not os.path.isdir(dest_py_folder):
        os.mkdir(dest_py_folder)

    with open(list_filename) as f:
        for line in f:
            line = line.strip()
            # skip comments
            if len(line) < 1 or line[0] == '#':
                continue

            if line == "maspy":
                if not copy_files(line, bin_path, dest_lib_folder):
                    print("Error! Not found", line)
                    return False
                continue

            if line.endswith(".py"):
                if not copy_files(line, py_path, dest_py_folder):
                    if not copy_files(line, py_path2, dest_py_folder):
                        print("Error! Not found", line)
                        return False
                continue

            found1 = copy_files(line, lib_path, dest_lib_folder)
            found2 = copy_files(line + ".so", lib_path, dest_lib_folder)

            if not found1 and not found2:
                print("Not found",line)  # Just warning

    return True
