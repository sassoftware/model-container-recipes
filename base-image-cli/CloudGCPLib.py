#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import docker
import os

PROVIDER_NAME = 'GCP'


class CloudGCPLib(object):
    def __init__(self, config, docker_client):
        self.key_file = config.get(PROVIDER_NAME, 'service.account.keyfile')
        self.project = config.get(PROVIDER_NAME, 'project.name')
        self.docker_client = docker_client
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.key_file

    #
    # login google container registry
    # return gcp gcr registry url
    #
    def login(self):
        if self.key_file is None:
            print("Please specify GCP token key file!")
            return None
        if self.project is None:
            print("Please specify the project name in GCP!")
            return None

        print('Login into GCP GCR...')

        with open(self.key_file, 'r') as myfile:
            password = myfile.read().replace('\n', '')  # remove line break!
        # print(password)

        username = "_json_key"
        registry = "https://gcr.io/v2/" + self.project

        # print(username, password, registry)
        try:
            self.docker_client.login(username, password, registry=registry)
        except docker.errors.APIError as err:
            print("Failed to login GCP GCR! Please check your gcloud configuration!")
            print(str(err))
            return None
        print("Login GCP GCR succeeded!")
        return "https://gcr.io/" + self.project
