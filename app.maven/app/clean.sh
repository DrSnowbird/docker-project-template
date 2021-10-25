#!/bin/bash

set -e 

ORGANIZATION=${ORGANIZATION:-openkbs}
PROJECT=${PROJECT:-myproj}
APPLICATION_NAME=${PWD##*/}
APP_VERSION=${APP_VERSION:-1.0.0}

## Base image to build this container
FROM_BASE=${FROM_BASE:-centos:8}
imageTag=${imageTag:-"${ORGANIZATION}/${APPLICATION_NAME}"}

## Docker Registry (Private Server)
#REGISTRY_HOST=${REGISTRY_HOME:-registry01.openkbs.org:5000}
#REGISTRY_IMAGE=${REGISTRY_HOST}/${imageTag}
VERSION=${APP_VERSION}-$(date +%Y%m%d)

###################################################
#### ---- Top-level build-arg arguments ----
###################################################
BUILD_ARGS="${BUILD_ARGS} --build-arg VERSION=${VERSION}"
BUILD_ARGS="${BUILD_ARGS} --build-arg ORGANIZATION=${ORGANIZATION}"
BUILD_ARGS="${BUILD_ARGS} --build-arg PROJECT=${PROJECT}"
BUILD_ARGS="${BUILD_ARGS} --build-arg FROM_BASE=${FROM_BASE}"

MY_DIR=$(dirname "$(readlink -f "$0")")

if [ $# -lt 1 ]; then
    echo "------------- Clean up both Container and Images -------------"
    echo "Usage: "
    echo "  ${0} [<container_shell_command>]"
    echo "e.g.: "
    echo "  ${0} tensorflow-python3-jupyter "
    echo "  ${0} "
    echo "      (empty argument will use default the current git container name to clean up)"
fi

###################################################
#### ---- Change this only to use your own ----
###################################################
baseDataFolder="$HOME/data-docker"

###################################################
#### **** Container package information ****
###################################################
DOCKER_IMAGE_REPO=`echo $(basename $PWD)|tr '[:upper:]' '[:lower:]'|tr "/: " "_" `

## -- transform '-' and space to '_' 
#instanceName=`echo $(basename ${imageTag})|tr '[:upper:]' '[:lower:]'|tr "/\-: " "_"`
instanceName=`echo $(basename ${imageTag})|tr '[:upper:]' '[:lower:]'|tr "/: " "_"`

echo "---------------------------------------------"
echo "---- Clean up the Container for ${imageTag}"
echo "---------------------------------------------"

if [ $1 ]; then
    imageTag="$1"
fi

containers=`docker ps -a | grep ${imageTag} | awk '{print $1}' `

if [ $containers ]; then
    docker rm -f $containers
fi

for IMAGE_ID in `docker images -a | grep ${imageTag} | awk '{print $3}' `; do
    children=$(docker images --filter since=${IMAGE_ID} -q)
    if [[ ! $children == *"No such image"* ]]; then
        id=$(docker inspect --format='{{.Id}} {{.Parent}}' $children |cut -d':' -f2|cut -c-12)
        if [ "$id" != "" ]; then
            docker rmi -f $id
        fi
    fi
done


