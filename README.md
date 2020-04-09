# Model Container Recipes

### Contents
* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Getting Started](#getting-started)

## Overview
The scripts in this repository enable users to create base images for their models, as well as model container images built using these base images. The containerized model images can be validated and deployed as containers using Kubernetes with these tools. The Docker Container Registry and Google Container Registry cloud platforms are supported, and we are working toward supporting other cloud platforms, such as Amazon Web Services and Azure. 

_**Note:** For information about creating base images for use with either SAS Model Manager or SAS Open Model Manager, see [Model Containerization](https://github.com/sassoftware/open-model-manager-resources/tree/master/addons#model-containerization) in the Open Model Manager Resources GitHub repository._ 

### Prerequisites
Here are the products and solutions that are currently supported:
* SAS Viya
* Single installed Linux machine
* Single tenant
* Python 3.4+
* Cloud Provider -- Google Cloud Platform, Amazon Web Services, Microsoft Azure
* Base images for R and Python 3 

It is recommended that the scripts be downloaded onto the same machine where SAS Viya is installed, and that the system user be set to `sas` instead of `root`. You can set the user to `sas` using the following command:
```
$ su - sas
```

## Installation

#### Python
The system user must have Python 3.x installed and set in their environment path. You can check the version of Python that is running with the following command:
```
python --version
```

In addition, use pip to install the following packages for Python 3:

```
$ pip install docker --user
$ pip install kubernetes
$ pip install python-slugify
```
You can check if a package has already been installed by executing the following command:
```
$ pip show <package>
```


#### Docker
The system user must also have [Docker Community Edition](https://www.docker.com/products/container-runtime). To install, use the following commands:

```
$ sudo yum install -y yum-utils \
device-mapper-persistent-data \
lvm2

$ sudo yum-config-manager \
--add-repo \
https://download.docker.com/linux/centos/docker-ce.repo

$sudo yum install -y docker-ce docker-ce-cli containerd.io

$sudo systemctl enable docker.service

$ sudo systemctl start docker.service
```

If a 'docker' group does not already exist, create one using the following command: 
Note: The previous install commands should have created a 'docker' group.

```
$ sudo groupadd docker
```
Add the 'sas' user to the 'docker' group
```
$ sudo usermod -aG docker sas
```

### Download Model Container Recipes
Download the source code from the Model Container Recipes Git repository. 


If the SAS Viya home directory is not `/opt/sas/viya`, edit the property value `viya.installation.dir` in the `config.properties` file. If it has not already been done, switch the system user to `sas` with the following command:
```
su - sas
```
---
## Getting Started

### Cloud Provider Configuration
We currently support 3 different Cloud Providers for use with our model container recipes. For information about configuring your Cloud Provider and Cloud Settings properly, please refer to the appropriate configuration guide from the options below:

* [Google Cloud Platform](./GCP_configuration_guide.md)
* [Amazon Web Services](./AWS_configuration_guide.md)
* [Microsoft Azure](./Azure_configuration_guide.md)

### Properties Files
If this is your first time using the utility, you must complete the required fields within the `config.properties` file. This file is located within the following directories: `base-image-cli` and `model-image-cli`. For more information, see the [base image folder](base-image-cli/) and the [model image folder](model-image-cli/).

If you have already configured your properties files, learn how to [create a base image](base-image-cli/) or [create and use a model image](model-image-cli/) by reviewing the respective READMEs.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

