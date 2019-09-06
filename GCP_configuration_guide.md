# Model Container Recipes Configuration Guide - Google Cloud Platform (GCP)

## Overview

This document contains steps for configuring model container recipes for Google Cloud Platform (GCP).

### Terminology
GCR - Google Container Registry

GKE - Google Kubernetes Engine

## Configuration Steps

To configure Google Cloud Platform (GCP), complete the following steps:
1. Create an account and download a service account key in JSON format.
2. Log in to the [GCP Console](https://console.cloud.google.com/). 
3. Select **APIs & Services > Credentials** from the navigation menu.
3. Click **CREATE** and select **Service account key**.
4. Specify the service account in which you want to obtain a key for and the key type as JSON.
5. Download the JSON file and name it `gcr_key.json`.
6. Copy `gcr_key.json` to the proper directories as specified in your config.properties files.
7. Install the [GCP Client](https://cloud.google.com/sdk/docs/#rpm).

### Enable APIs
Enable the `Container Registry` and `Google Kubernetes Engine` APIs from the GCP Console.

### Docker Configuration
In the command line enter the following commands to authorize the Docker client:

```
$ gcloud auth configure-docker
$ gcloud auth login
```

#### Verification
Verify that the Google authorization token file (gcr_key.json) has been downloaded in the directory.

Log in to the Docker client for GCP:

```
  $ cat gcr_key.json | docker login -u _json_key --password-stdin https://gcr.io
```

### Kubernetes Configuration
1. Select a zone, cluster name, number of worker nodes, and so on.
2. Create a Kubernetes cluster in web console.
3. Update the Kubernetes configuration with the following command:
```
$ export GOOGLE_APPLICATION_CREDENTIALS=gcr_key.json
$ gcloud container clusters get-credentials <cluster name> --zone <zone> --project <project name>
$ kubectl get nodes
```
Note: You can also verify the Kubernetes contexts with this command:
```
$ kubectl config get-contexts
```
4. Write down the gcloud cluster context name, which is required in model-image-cli/config.properties.

#### Update Firewall Rule
Kubernetes is using node port between 30000 and 32767. So create a firewall rule as:
```
$ gcloud compute firewall-rules create gke-rule --allow tcp:30000-32767
```
