# Model Container Recipes - Base Image Creation

## Overview
This 'Base Image Creation' recipe is used to help users to generate the base container 
images, which can be used during model image generation.

Here are the types of model base images that are currently supported:
* Python 2 base image is used for scoring Python 2 models
* Python 3 base image is used for scoring Python 3 models
* R base image is used for scoring R models

### Installation

Use Git tools to download current project from the Git repository.  

## Getting Started

Assuming that the project has been downloaded and stored in the <b>/opt/sas/model-container-recipes</b> directory, perform the following steps:<br>
1. Switch to the installation directory.
```
  $ cd /opt/sas/model-container-recipes
  $ cd base-image-cli
```
2. Verify that your chosen cloud provider is configured and authenticated correctly. For more information, see the configuration guides in the parent directory, `model-container-recipes`.

3. Modify the `config.properties` file, if necessary.
  
  [Config]
  * `provider.type` - the run-time provider type
  * `viya.installation.dir` - the path to the directory where SAS Viya is installed; this should be changed if the path is not `/opt/sas/viya`
  (Optional for this release)

  [GCP]
  * `project.name` - the name of the project on Google Cloud Platform
  * `service.account.keyfile` - the name of the JSON file containing the service account key to authenticate your GCP account; this file should reside in the `base-image-cli` directory

  [Azure]
  * `resource.group` - the name of the Azure resource group
  * `azure.container.registry` - the name of the Azure Container Registry

  [AWS]
  * `access.key.id` - the Amazon Web Services (AWS) Access Key ID
  * `Secret.access.key` - the AWS Secret Access Key
  * `region` - the region or zone selected  

* For more information about the command line syntax, run the following command from the `base-image-cli` directory:
```
  $ python base_image_generation.py -h
```

* For each base image generation and testing, see the documentation within the following folders:
  - [Python 2 or 3](python_base/)
  - [R](r_base/)

## FAQs
*None currently available.*

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources

* [Docker Documentation](https://docs.docker.com/)
* [SAS License Assistance](https://support.sas.com/en/technical-support/license-assistance.html)
* [SAS Software Purchase](https://www.sas.com/en_us/software/how-to-buy.html)
* [SAS Software Trial](https://www.sas.com/en_us/trials.html)
