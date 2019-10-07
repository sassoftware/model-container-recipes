# Model Containerization - Base Image Creation - MASPY

## Getting Started

**Note:** The SAS Micro Analytic Service Python (MASPY) base image is used for scoring SAS DS2 models and is not available in current version.

1. Read the documentation from the parent directory and prepare the environment.

2. Generate MASPY base image by running the following command:
```
  $ python base_image_generation.py maspy
```
This should result in the following output:

```
Loading configuration properties...
Login into AWS ECR...
Login AWS ECR succeeded!
  viya.installation.dir: /opt/sas/viya
  provider.type: AWS
  base.repo: 12345678.dkr.ecr.us-east-1.amazonaws.com/
===================================
Gathering MAS dependency libraries...
Building base image...
Tag the image into a repository. Image ID sha256:fcafb9dacb
Docker repository URL:  12345678.dkr.ecr.us-east-1.amazonaws.com/
Creating AWS ECR repo...
Checking remote repo maspy-base in AWS ECR...
AWS ECR maspy-base doesn't exist
Creating remote repo maspy-base in AWS ECR...
Pushing to repo...
Pushed. Please verify it at container repository
Model image URL: 12345678.dkr.ecr.us-east-1.amazonaws.com/maspy-base:latest
Remote Image Url 12345678.dkr.ecr.us-east-1.amazonaws.com/maspy-base:latest
Succeed.

```

For more information, refer to the FAQs in the Base Image Creation [README](../README.md).

## Test

You can test the generated MAS base image with provided analytic store (ASTORE) model. 
The test script in the test folder does the following:
* temporarily generates a local model image from local MAS base image
* launches a container instance via 'docker run'
* performs scoring in the container instance
* retrieves the score results and display
* terminates the container instance
* deletes the temporary model image
    
```
  $ cd model-container-recipes
  $ cd base-image-cli/maspy_base/test
  $ chmod 755 test_model_image.sh
  $ ./test_model_image.sh  
```
## License

This project is licensed under the [Apache 2.0 License](LICENSE).
