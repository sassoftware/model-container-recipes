#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import subprocess

PROVIDER_NAME = 'Azure'


class CloudAzureLib(object):
    def __init__(self, config, docker_client):
        self.registry_name = config.get(PROVIDER_NAME, 'azure.container.registry')
        self.docker_client = docker_client

    #
    # login azure container registry
    # return acr registry url
    #
    def login(self):
        if self.registry_name is None:
            print("Please specify registry name!")
            return None

        print('Login into Azure Container Registry...')
        registry = self.registry_name + ".azurecr.io"

        try:
            # cmd_str = "az acr login --name " + self.registry_name
            # result_str = os.popen(cmd_str).read()
            args = ("az", "acr", "login", "--name", self.registry_name)
            p_open = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p_stdout, p_stderr = p_open.communicate()
            result_str = p_stdout.decode("utf-8")
            if 'Login Succeeded' not in result_str:
                print("Failed to login Azure Container Registry! Please check your Azure configuration!")
                print(result_str)
                if p_stderr:
                    error_str = p_stderr.decode("utf-8")
                    print(error_str)
                return None

            print("Login Azure Container Registry succeeded!")
            return registry.lower()
        except Exception as err:
            print("Failed to login Azure Container Registry! Please check your Azure configuration!")
            print(str(err))
            return None
