#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#


__version__ = '1.0'


import os
from shutil import copyfile

base_dir = os.path.dirname(os.path.realpath(__file__))


#
# Prepare Dockerfile in the template for the correct Python version
#
def prepare_dockerfile(python_version):
    print("Preparing Dockerfile based on Python version...")

    src_file = os.path.join(base_dir, "Dockerfile." + python_version)

    files_folder = os.path.join(base_dir, "files")
    dest_file = os.path.join(files_folder, "Dockerfile")

    if os.path.isfile(src_file):
        # print("Copying", src_file, "To", dest_file)
        copyfile(src_file, dest_file)
        return True
    else:
        print(src_file, "doesn't exist")
        return False
