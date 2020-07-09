#!/bin/bash
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

echo Building model image for a test model in local...
echo ====================
cd model
docker image build -t  test_model:latest .

echo Removing container instance if exists...
echo ====================
docker container rm -f test_model

cd ..
echo    
echo Starting container instance as a daemon...
echo ====================
docker container run --name test_model -d -p 8188:8080 -ti test_model:latest &
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
execution_id=`curl -s --form file=@test.csv --form press=OK localhost:8188/executions | jq -r '.id'`
# remove the trailing spaces
execution_id=`echo $execution_id | sed -e 's/\r//g'`

echo    
echo execution id is $execution_id
echo sleep 5s for execution
echo ====================
sleep 5

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
echo Deleting image...
echo ====================
docker image rm -f test_model:latest


echo    

