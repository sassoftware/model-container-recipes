# Model Container Recipes Configuration Guide - Amazon Web Services (AWS)

## Overview

This document contains steps for configuring model container recipes for Amazon Web Services (AWS).

### Terminology
ECR - Amazon Elastic Container Registry

EKS - Amazon Elastic Kubernetes Service

### Permissions
Due to the requirements of creating an Amazon Kubernetes cluster, the AWS user account must have the following permissions: 

- Read and Write to ECR 
- Create an IAM role
- Assign policy to IAM role
- Create a VPC stack
- Create an EKS cluster
- Create an EKS worker nodes stack
- Change a security group of the worker nodes
- Enable worker nodes to join EKS cluster

## Configuration Steps
### Install AWS CLI
1. Download and install AWS CLI.
2. Run the following command to login aws user
```
$ aws configure
```
3. Input AWS Access Key ID, Secret Access Key and region info
 
### Docker Configuration
1. In the command line enter the following commands to authorize the Docker client:
```
$ aws ecr get-login --no-include-email
```
2. Copy the whole output and run it as a new command which must begin with 'docker login -u AWS -p'.

### Kubernetes Configuration

1. Follow the [Getting Started steps](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) to create 
the EKS cluster and worker nodes. Do not forget to enable the worker nodes to join the EKS cluster in the end.

2. Download [aws-iam-authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html) and store it in the current directory or path.

3. Update Kubernetes config with the following command:
```
$ aws eks --region <zone> update-kubeconfig --name <cluster name>
$ kubectl get nodes
```
Note: You can also verify the Kubernetes contexts with this command:
```
$ kubectl config get-contexts
```
4. Write down the cluster context name, which is required in model-image-cli/config.properties.

#### Update VPC Rule
Kubernetes is using node port between 30000 and 32767. Make sure that your installation machine is able to access those ports in AWS VPC subnets.


