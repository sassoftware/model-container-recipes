#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import base64
import docker
import boto3
import os


PROVIDER_NAME = 'AWS'


class CloudAWSLib(object):

    def __init__(self, config, docker_client):
        # not using aws profile any more
        # self.aws_profile = config.get(PROVIDER_NAME, 'aws.profile')
        # os.environ["AWS_PROFILE"] = self.aws_profile
        self.access_key_id = config.get(PROVIDER_NAME, 'access.key.id')
        self.secret_access_key = config.get(PROVIDER_NAME, 'secret.access.key')
        self.region = config.get(PROVIDER_NAME, 'region')

        self.docker_client = docker_client
        self.ecr_client = boto3.client(
            'ecr',
            region_name = self.region,
            aws_access_key_id = self.access_key_id,
            aws_secret_access_key = self.secret_access_key)

        self.auth_config_payload = None

    # return aws ecr registry url and docker client
    def login(self):
        print('Login into AWS ECR...')
        token = self.ecr_client.get_authorization_token()
        username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
        self.auth_config_payload = {'username': username, 'password': password}
        registry = token['authorizationData'][0]['proxyEndpoint']
        # print(username, password, registry)
        try:
            self.docker_client.login(username, password, registry=registry)
        except docker.errors.APIError as err:
            print("Failed to login AWS ECR! Please check your AWS configuration!")
            print(str(err))
            return None
        print("Login AWS ECR succeeded!")
        return registry

    # return true if exists
    def check_ecr_repo(self, name):
        print('Checking remote repo', name, 'in AWS ECR...')
        try:
            response = self.ecr_client.describe_repositories(repositoryNames=[name])
        except:
            print("AWS ECR", name, "doesn't exist")
            return False
        return True

    def create_ecr_repo(self, name):
        if not self.check_ecr_repo(name):
            print('Creating remote repo', name, 'in AWS ECR...')
            try:
                self.ecr_client.create_repository(repositoryName=name)
            except:
                print('Failed to create AWS ECR', name)
                return False
        return True

