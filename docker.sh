#!/bin/bash

CONTAINER="iii-ai-flow-hub-api"
DOCKER_REPO="iiicondor/$CONTAINER"
VERSION="1.0.1"
MESSAGE="[Lisa]"

docker build -t $DOCKER_REPO:$VERSION .
docker push $DOCKER_REPO:$VERSION

#echo "[`date "+%Y-%m-%d %H:%M:%S"`] $DOCKER_REPO:$VERSION => {$MESSAGE}" >> ImageInfo.txt
#echo "[`date "+%Y-%m-%d %H:%M:%S"`] $DOCKER_REPO:$VERSION " >> imageInfo.txt

docker rmi -f $(docker images | grep $DOCKER_REPO | awk '{print $3}')
docker image prune -f

#docker build -t iiicondor/iii-ai-flow-hub-api:1.0.1 . 
#docker push iiicondor/iii-ai-flow-hub-api:1.0.1