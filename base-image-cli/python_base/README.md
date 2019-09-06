# Model Containerization - Base Image Creation - Python

## Getting Started

1. Read the documentation from the parent directory and prepare the environment.

2. Generate the Python base image, using the following `commands`.

```
  $ python base_image_generation.py python -h
  usage: base_image_generation.py python [-h] [--version VERSION]

  optional arguments:
    -h, --help            show this help message and exit
    --version VERSION, -v VERSION
                          Python Version: 2 or 3

```
Note: The default Python base image is built using Python 3, but you can specify the Python version as either 2 or 3 using the optional argument `--version`. 

Here is an example of generating a Python 2 base image and the resulting output:

```
$ python base_image_generation.py python --version 2
Loading configuration properties...
Login into AWS ECR...
Login AWS ECR succeeded!
  viya.installation.dir: /opt/sas/viya
  provider.type: AWS
  base.repo: 12345678.dkr.ecr.us-east-1.amazonaws.com/
===================================
Preparing Dockerfile based on Python version...
Building base image...
Tag the image into a repository. Image ID sha256:ba1141f681
Docker repository URL:  12345678.dkr.ecr.us-east-1.amazonaws.com/
Creating AWS ECR repo...
Checking remote repo python2-base in AWS ECR...
Pushing to repo...
Pushed. Please verify it at container repository
Model image URL: 12345678.dkr.ecr.us-east-1.amazonaws.com/python2-base:latest
Remote Image Url 12345678.dkr.ecr.us-east-1.amazonaws.com/python2-base:latest
Succeed.

```
For more information, refer to the FAQs in the Base Image Creation [README](../README.md).

## Test

You can test the generated Python base image with the provided Python pickle model (Python 3). 
The test script in the test folder does the following: 
* temporarily generates a local model image from the local Python base image (Python 3)
* launches a container instance via 'docker run'
* performs scoring in the container instance
* retrieves the score results and display
* terminates the container instance
* deletes the temporary model image
    
```
  $ cd model-container-recipes
  $ cd base-image-cli/python_base/test
  $ chmod 755 test_model_image.sh
  $ ./test_model_image.sh  
```

## Scope
The current release of Python3 base image installs Miniconda 3 with Python 3.6.7.
If a user's Python model has to use specific version of Python 3, please refer to 
Model Image Generation documentation to add extra dependencies in the requirements.json file under model content. 

The current release of Python2 base image installs Miniconda 2 with Python 2.7.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
