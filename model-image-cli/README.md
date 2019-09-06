# Model Container Recipes - Model Image Creation

## Overview


### Installation

Use Git tools to download the current project from the Git repository.

## Getting Started
Assume the project has been downloaded and stored in the directory <b>/opt/sas/model-container-recipes</b>.<br>
1. Switch to installation directory, using the following commands.

```
  $ cd /opt/sas/model-container-recipes
  $ cd model-image-cli
```

2. Verify that your chosen cloud provider is configured and authenticated correctly. For more information, see the configuration guides in the parent directory, `model-container-recipes`.

3. Modify the `config.properties` file if needed

  [Config]
  * `verbose` - set the verbose mode for debugging; default mode is False
  * `provider.type` - the run-time provider type
  * `viya.installation.dir` - the path to the directory where SAS Viya is installed; this should be changed if this path is not `/opt/sas/viya`
  * `model.repo.host` - the url, with http protocol, to the model repository

  [GCP]
  * `project.name` - the name of the project on Google Cloud Platform
  * `service.account.keyfile` - the name of the JSON file containing the service account key to authenticate your GCP account; this file should reside in the `base-image-cli` directory
  * `kubernetes.context` - the Kubernetes context

  [Azure]
  * `resource.group` - the name of the Azure resource group
  * `azure.container.registry` - the name of the Azure Container Registry
  * `kubernetes.context` - the Kubernetes context

  [AWS]
  * `access.key.id` - the AWS Access Key ID
  * `Secret.access.key` - the AWS Secret Access Key
  * `region` - the region or zone selected  
  * `kubernetes.context` - the Kubernetes context

To see more information about the command line syntax, run the following from the `model-image-cli` directory:
```
  $ python model_image_generation.py -h
  
  $ python model_image_generation.py <action> [-h]
```
For each action please refer to the User's Guide below.

### User's Guide
We currently support the ability to run each of the following `<action>` types from the command line: [`listmodel`](#listmodel), [`scorelog`](#scorelog), [`systemlog`](#systemlog), [`publish`](#publish), [`launch`](#launch), [`execute`](#execute), [`query`](#query), [`stop`](#stop), and [`score`](#score). 

#### listmodel

Arguments <br>
`<key>` <br>
This argument acts as a filter on the resulting list of models. Only models with names containing the `<key>` are shown. If `all` is passed as the argument, the resulting list consists of all of the models.

Result <br>
The `listmodel` action prints information about each model (i.e. the name, UUID, version, project name, score code type, and the image URL) from the list of models existing in the Model Repository and filtered by the `<key>`. 

To call this action use the following syntax:

```
$ python model_image_generation.py listmodel <key>
```

#### publish

Arguments <br>
`<type>` <br>
This argument indicates whether the user is providing a model UUID or file. Available types: `id`, `file`

`<id_or_filename>` <br>
This argument specifies either the UUID of the model or the name of the file containing the model content.

Result <br>
The `publish` action builds the container image with the given model and its dependencies and then pushes the container image to the model repository specified within the `config.properties` file. The container image URL is returned if this process completes without errors.

To call this action use the following syntax:

```
$ python model_image_generation publish <type> <id_or_filename>
```

#### launch

Arguments <br>
`<image_url>` <br>
This argument specifies the URL of a container image.

Result <br>
The `launch` action submits a request to Kubernetes to start a container instance of the model from the given image URL and returns the deployment name and service URL. 


To call this action use the following syntax:

```
$ python model_image_generation launch <image_url>
```

#### execute

Arguments <br>
`<service_url>` <br>
This argument provides the exposed service URL.

`<csv_file>` <br>
This argument indicates the name of the .csv file containing the test data.

Result <br>
The `execute` action performs scoring on the containerized instance of a model with a given input data file and returns the test ID from the score execution. 

To call this action use the following syntax:

```
$ python model_image_generation execute <service_url> <csv_file>
```

#### query

Arguments <br>
`<service_url>` <br>
This argument provides the exposed service URL.

`<test_id>` <br>
This argument specifies the test ID returned from a score execution.

Result <br>
The `query` action retrieves the results of a score execution by the given test ID and prints the first 5 lines of the results.

To call this action use the following syntax:

```
$ python model_image_generation query <service url> <test_id>
```

#### stop

Arguments <br>
`<deployment_name>` <br>
This argument provides the deployment name given by `launch` command.

Result <br>
The `stop` action submits a request to Kubernetes to terminate a container instance and delete the associated deployment. 


To call this action use the following syntax:

```
$ python model_image_generation stop <deployment_name>
```

#### score

Arguments <br>
`<image_url>` <br>
This argument specifies the URL of the container image.

`<csv_file>` <br>
This argument provides the name of the .csv file which contains the test data.

Result <br>
The `score` action runs the `launch`, `execute`, `query` and `stop` commands in batch. It launches the container instance in Kubernetes cluster, performs scoring on the container instance, retrieves the results, and terminates service and deployment in the end. 

To call this action use the following syntax:

```
$ python model_image_generation score <image_url> <csv_file>
```

#### scorelog

Arguments <br>
`<service_url>` <br>
This argument provides the exposed service URL.

`<test_id>` <br>
This argument specifies the test ID returned from a score execution.

Result <br>
The `scorelog` action retrieves the result log of a score execution by the given test ID and prints the first 5 lines of the results. 

To call this action use the following syntax:

```
$ python model_image_generation scorelog <service url> <test_id>
```

#### systemlog

Arguments <br>
`<service_url>` <br>
This argument provides the exposed service URL.

Result <br>
The `systemlog` action retrieves the system/gunicorn log from the container instance at the given service URL and prints the last 5 lines of the system log.

To call this action use the following syntax:

```
$ python model_image_generation systemlog <service_url>
```



## FAQs

Q: When providing a `filename` to the `publish` function, what should the model ZIP file contain? 

A: We suggest using the model ZIP file downloaded from SAS Model Manager. The model ZIP file referenced in the `publish` parameters must include a file `ModelProperties.json`, which contains information such as the model ID, model name, and the score code type.
If the model has external dependent file file, such as ASTORE file, Python pickle file or R .rda file, it must be included in the ZIP file manually.


Q: What should I do if my model has extra dependencies on software libraries or packages that are not included in the base image?

A: If your model relies on dependencies that are not supported by the provided base images, you should create a file named `requirements.json` within the model ZIP file. This file should contain the steps to create the extra dependencies as well as the command to run to install them. The script checks for a non-empty `requirements.json` file and add the step commands to the Dockerfile in order before building the model image.

The format of the requirements.json likes:
```
[
    {
        "step":"install openjdk1.8 devel",
        "command":"yum install -y java-1.8.0-openjdk-devel"        
    },
    {
        "step":"install h2o in anaconda",
        "command":"conda install -y -c h2oai h2o=3.22.0.2"
     }
 ]
``` 

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources
