# Model Container Recipes Configuration Guide - Microsoft Azure (Azure)

## Overview

This document contains steps for configuring model container recipes for Microsoft Azure (Azure).

### Terminology

ACR - Azure Container Registry

AKS - Azure Kubernetes Service

## Configuration Steps
### Install Azure CLI
1. Download and install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
2. Run the following command to login to Azure: 
```
$ az login
```
3. Configure your default subscription and default resource group.

```
$ az account set -s <your subscription name>
$ az configure --defaults group=<your resource group name>
```

### Docker Configuration
Create an Azure Container Registry (ACR) in the console by picking up a location, SKU, and so on.

In the command line enter the following commands to authorize the Docker client:
```
$ az configure --defaults acr=<acr name>
$ az acr login
```

Without setting default value, you can add --name <acr name> to the login command. Here is an example:
```
$ az acr login --name <acr name>
```

### Kubernetes Configuration
1. Create Azure Kubernetes Service in web console by setting proper workloads.
2. Update Kubernetes config with the following command:
```
$ az aks get-credentials --resource-group <resource group name> --name <cluster name>
$ kubectl get nodes
```
Note: You can also verify the Kubernetes contexts with this command:
```
$ kubectl config get-contexts
```
3. Write down the cluster context name, which is required in the model-image-cli/config.properties.
4. Grant access for AKS cluster to pull images from ACR by assigning AcrPoll role
```
$ SP_ID=$(az aks show --resource-group <resource group name> --name <cluster name> --query servicePrincipalProfile.clientId -o tsv)

$ ACR_ID=$(az acr show --resource-group <resource group name> --name <ACR name> --query "id" --output tsv)

$ az role assignment create --assignee $SP_ID --scope $ACR_ID  --role acrpull

```
5. In Azure web console enable public IP for each VM in the AKS cluster
6. Add security rule in Network Security Group for AKS container access
Kubernetes is using node port between 30000 and 32767. Here is an example:
```
$ CLUSTER_RESOURCE_GROUP=$(az aks show --resource-group <resource group> --name <cluster name>  --query nodeResourceGroup -o tsv)

$ AKS_NSG=$(az network nsg list --resource-group $CLUSTER_RESOURCE_GROUP -o json | jq .[0].name)

$ az network nsg rule create --resource-group $CLUSTER_RESOURCE_GROUP  --nsg-name $AKS_NSG  --name Access_AKS --access Allow --protocol Tcp --direction Inbound --priority 100 --source-address-prefix "<ip subnet allowed to access containers>" --source-port-range "*" --destination-address-prefix "*" --destination-port-range "30000-32767"

``` 


