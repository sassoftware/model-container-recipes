#!/bin/bash
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

#
# The script is used to test the generated model image
# However it launches container instance in local system instead of Kubernetes system in the cloud
#
if [ "$#" -ne 2 ]; then
    echo " "
    echo "Usage: ./test_model_image.sh <image_url> <test_csv_file>"
    echo "Arguments:"
    echo "   image_url - input local image name or remote container image url"
    echo "   test_csv_file - test file in csv format"
    echo " "
    echo "You can find the images by issue 'docker image ls'"
    echo " "
    exit
fi

image_url=$1
input_file=$2

echo    
echo Starting container instance as a daemon...
echo ====================
docker container run --name test_model -d -p 8188:8080 -ti $image_url &
echo    
echo Checking container health...
echo ====================
sleep 5
token=`curl -s localhost:8188/`
if [ $token == 'pong' ]
then
    echo "Instance is up..."
else
    echo "Something is wrong with container instance."
    echo "Please use 'docker exec -it test_model bash' to diagnose"
    echo "To delete failed container instance, use 'docker container rm -f test_model'"
    exit
fi

echo   
echo    
echo Upload sample data to perform scoring in the container...
echo ====================
execution_id=`curl -s --form file=@$input_file --form press=OK localhost:8188/executions | jq -r '.id'`
echo    
echo execution id is $execution_id
echo ====================

echo    
echo Getting result back if execution succeeds...
echo ====================
curl -s -o result.csv localhost:8188/query/$execution_id
curl -s -o result.log localhost:8188/query/$execution_id/log
curl -s -o system.log localhost:8188/system/log


echo    
echo Here is the results if the file is retrieved
echo ====================
cat result.csv

echo
echo Here is the execution log
echo ====================
cat result.log

echo
echo Here is the last 5 lines of the system log
echo ====================
tail -5 system.log

echo    
echo Stop and delete the test container...
echo ====================
docker container stop test_model
docker container rm test_model

rm -f result.csv
rm -f result.log
rm -f system.log



echo    

