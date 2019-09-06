#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


__version__ = '1.0'

import argparse
from BaseImageLib import *

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Base Image Generation  CLI')
    subparsers = parser.add_subparsers(title="actions", dest="action")

    parser_python= subparsers.add_parser("python", help="Generate python base image")
    # default is Python 3
    parser_python.add_argument('--version','-v', help='Python Version: 2 or 3', type=int, default=3)

    parser_r = subparsers.add_parser("r", help="Generate R base image")

    args = parser.parse_args()
    kwargs = vars(args)

    if kwargs["action"] is None:
        parser.print_help()
        exit(0)

    try:
        # print(globals())
        globals()[kwargs.pop('action')](**kwargs)
    except RuntimeError as err:
        print("Runtime Error: ", err)


