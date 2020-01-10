#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import configparser
import os
import docker
from CloudAWSLib import CloudAWSLib
from CloudAzureLib import CloudAzureLib
from CloudGCPLib import CloudGCPLib
import traceback
from shutil import copyfile
from python_base import pythonbase_lib
from r_base import rbase_lib


class BaseImageLib(object):
    def __init__(self):
        self.docker_client = docker.from_env()
        # initial cloud libraries
        self.mm_docker_aws = None
        self.mm_docker_gcp = None
        self.mm_docker_azure = None

        # initial default variables
        self.provider = 'Dev'
        self.base_repo = "docker.sas.com/"
        self.viya_install_dir = '/opt/sas/viya'

    #
    # copy file from source folder to destination folder
    #
    def copy_files(self, file_name, src_path, dest_path):
        src_file = os.path.join(src_path, file_name)
        if os.path.isfile(src_file):
            dest_file = os.path.join(dest_path, file_name)
            # print("Copying", src_file, "to", dest_file)
            copyfile(src_file, dest_file)
            return True
        return False
        
    #
    # build Docker image
    #
    def build_base_image(self, base_lib, tag_name):
        # build local image with docker daemon
        dest_folder = os.path.join(base_lib.base_dir, "files")
        version = base_lib.__version__
    
        print("Building base image...")
        local_tag = tag_name + ":" + version
        my_image, _ = self.docker_client.images.build(path=dest_folder, tag=local_tag, nocache=True)
        # also tag it as latest version
        my_image.tag(tag_name, "latest")
    
        print("Tag the image into a repository. Image ID", my_image.short_id)
        remote_version_latest = self.push_to_repo(my_image, tag_name, version)
        print("Remote Image Url", remote_version_latest)
        
    #
    # push the image to remote repo
    #
    def push_to_repo(self, my_image, tag_name, version_id):
        repo = self.base_repo + tag_name
    
        print("Docker repository URL: ", self.base_repo)
    
        # default is latest, always using latest
        remote_version_tag = repo + ':' + version_id
        remote_version_latest = repo + ':latest'
    
        if my_image.tag(repo, version_id) is False:
            raise RuntimeError("failed on tagging")
    
        if my_image.tag(repo, "latest") is False:
            raise RuntimeError("failed on tagging remote latest")

        if self.provider == 'AWS':
            print("Creating AWS ECR repo...")
            if not self.mm_docker_aws.create_ecr_repo(tag_name):
                raise RuntimeError("Failed on creating ecr repo")
    
        print("Pushing to repo...")

        ret_str = self.docker_client.images.push(remote_version_tag)
        if 'errorDetail' in ret_str:
            print("Error: ", ret_str)
            raise RuntimeError("Failed on push")
    
        ret_str = self.docker_client.images.push(remote_version_latest)
        if 'errorDetail' in ret_str:
            print("Error: ", ret_str)
            raise RuntimeError("Failed on push")
    
        print("Pushed. Please verify it at container repository")
        print("Model image URL:", remote_version_latest)
        return remote_version_latest    
    
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
    
    # load configuration from file
    # if provider value is passed in, it will overwrite the setting in config.properties
    # return False if failed
    def init_config(self, p=None):
        config_file_name = "config.properties"
    
        print("Loading configuration properties...")
    
        try:
            config = configparser.RawConfigParser()
            config.read(config_file_name)
    
            if config.has_option('Config', 'viya.installation.dir'):
                self.viya_install_dir = config.get('Config', 'viya.installation.dir')
            else:
                self.viya_install_dir = '/opt/sas/viya'
    
            if p is not None:
                self.provider = p
            else:
                if config.has_option('Config', 'provider.type'):
                    self.provider = config.get('Config', 'provider.type')
                else:
                    self.provider = 'Dev'

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
                registry = config.get(self.provider, 'base.repo')

            if registry is None:
                return False

            self.convert_base_repo(registry)
    
        except:
            print("Error loading configuration from", config_file_name,"file! Double-check Docker daemon or other environment.")
            print(traceback.format_exc())
            return False
    
        print('  viya.installation.dir:', self.viya_install_dir)
        print('  provider.type:', self.provider)
        print('  base.repo:', self.base_repo)
    
        print("===================================")
        return True    


#
# Generate MASPY base image
#
def maspy():
    print("Not available in this release!")


#
# Generate Python base image
#
def python(version):
    base_image_lib = BaseImageLib()
    if not base_image_lib.init_config():
        print("Error:", "Failed in configuration initialization")
        exit(1)

    if version < 3 or version > 3:
        print("Error:", "Incorrect Python major version. Should be 3")
        exit(1)

    python_version = str(version)
    if not pythonbase_lib.prepare_dockerfile(python_version):
        print("Failed!")
        exit(1)

    base_tag = 'python' + python_version + "-base"

    base_image_lib.build_base_image(pythonbase_lib, base_tag)
    print("Succeed.")


#
# Generate R base image
#
def r():
    base_image_lib = BaseImageLib()
    if not base_image_lib.init_config():
        print("Error:", "Failed in configuration initialization")
        exit(1)

    base_image_lib.build_base_image(rbase_lib, "r-base")
    print("Succeed.")

