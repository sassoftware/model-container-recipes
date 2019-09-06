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
from ModelImageLib import ModelImageLib

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Model Container Generation CLI')
    subparsers = parser.add_subparsers(title="actions", dest="action")

    parser_list = subparsers.add_parser("listmodel")
    parser_list.add_argument("key", help='partial model name or \'all\'')
    parser_list.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")

    parser_publish = subparsers.add_parser("publish")
    parser_publish.add_argument("type", help='Value type', choices=["id", "file"])
    parser_publish.add_argument("id_or_filename", help='Model UUID or Model file')
    parser_publish.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")

    parser_launch = subparsers.add_parser("launch")
    parser_launch.add_argument("image_url", help='Docker image URL')
    parser_launch.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")    

    parser_execute = subparsers.add_parser("execute")
    parser_execute.add_argument("service_url", help='The exposed service URL')
    parser_execute.add_argument("csv_file", help='The test data in csv format')
    parser_execute.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")

    parser_query = subparsers.add_parser("query")
    parser_query.add_argument("service_url", help='The exposed service URL')
    parser_query.add_argument("test_id", help='The test id returned from score execution')
    parser_query.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")
    
    parser_stop = subparsers.add_parser("stop")
    parser_stop.add_argument("deployment_name", help='The deployment name from score execution')
    parser_stop.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")
    
    parser_score = subparsers.add_parser("score")
    parser_score.add_argument("image_url", help='Docker image URL')
    parser_score.add_argument("csv_file", help='The test data in csv format')
    parser_score.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")
    
    parser_log = subparsers.add_parser("scorelog")
    parser_log.add_argument("service_url", help='The exposed service URL')
    parser_log.add_argument("test_id", help='The test id returned from score execution')
    parser_log.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")
    
    parser_syslog = subparsers.add_parser("systemlog")
    parser_syslog.add_argument("service_url", help='The exposed service URL')
    parser_syslog.add_argument("-v", "--verbose", help='turn on verbose', action="store_true")

    args = parser.parse_args()
    kwargs = vars(args)

    image_lib = ModelImageLib()

    if "verbose" in kwargs:
        if args.verbose:
            image_lib.set_verbose(True)
        del kwargs["verbose"]

    if kwargs["action"] is None:
        parser.print_help()
        exit(0)

    if not image_lib.init_config():
        exit(1)
    
    try:
        action = kwargs.pop('action')
        method_to_call = getattr(image_lib, action)
        method_to_call(**kwargs)
    except RuntimeError as err:
        print("Runtime Error: ", err)
