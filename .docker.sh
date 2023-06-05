#!/bin/bash

# 正式用
CONTAINER="iii-automl-api"
DOCKER_REPO="iiicondor/$CONTAINER"
VERSION="0.0.22"
MESSAGE="[Lisa]"

docker build -t $DOCKER_REPO:$VERSION .
docker push $DOCKER_REPO:$VERSION

#echo "[`date "+%Y-%m-%d %H:%M:%S"`] $DOCKER_REPO:$VERSION => {$MESSAGE}" >> ImageInfo.txt
#echo "[`date "+%Y-%m-%d %H:%M:%S"`] $DOCKER_REPO:$VERSION " >> imageInfo.txt

docker rmi -f $(docker images | grep $DOCKER_REPO | awk '{print $3}')
docker image prune -f

#docker build -t iiicondor/iii-automl-api:0.0.6 . 
#docker push iiicondor/iii-automl-api:0.0.6