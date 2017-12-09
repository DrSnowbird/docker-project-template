#!/bin/bash -x

if [ $# -lt 1 ]; then
    echo "Usage: "
    echo "  ${0} <image_tag>"
fi

###################################################
#### **** Container package information ****
###################################################
MY_IP=`ip route get 1|awk '{print$NF;exit;}'`
DOCKER_IMAGE_REPO=`echo $(basename $PWD)|tr '[:upper:]' '[:lower:]' `
imageTag=${1:-"openkbs/${DOCKER_IMAGE_REPO}"}
#PACKAGE=`echo ${imageTag##*/}|tr "/\-: " "_"`
PACKAGE="${imageTag##*/}"
baseDataFolder="$HOME/data-docker"

###################################################
#### ---- Volumes to be mapped (change this!) -----
#################################################### (examples - some local vars)
# (exampples)
# IDEA_PRODUCT_NAME="IdeaIC2017"
# IDEA_PRODUCT_VERSION="3"
# IDEA_INSTALL_DIR="${IDEA_PRODUCT_NAME}.${IDEA_PRODUCT_VERSION}"
# IDEA_CONFIG_DIR=".${IDEA_PRODUCT_NAME}.${IDEA_PRODUCT_VERSION}"
# IDEA_PROJECT_DIR="IdeaProjects"
# VOLUMES="${IDEA_CONFIG_DIR} ${IDEA_PROJECT_DIR}"

# ---------------------------
# MANDATORY Variable: VOLUMES
# ---------------------------
VOLUMES="data workspace"

#########################################################################################################
######################## DON'T CHANGE LINES STARTING BELOW (unless you need to) #########################
#########################################################################################################
LOCAL_VOLUME_DIR="${baseDataFolder}/${PACKAGE}"
DOCKER_VOLUME_DIR="/home/developer"

###################################################
#### ---- Function: Generate volume mappings  ----
####      (Don't change!)
###################################################
VOLUME_MAP=""
#### Input: VOLUMES - list of volumes to be mapped
function generateVolumeMapping() {
    for vol in $VOLUMES; do
        echo "$vol"
        if [[ $vol == "/"* ]]; then
            # -- non-default /home/developer path; then use the full absolute path --
            VOLUME_MAP="${VOLUME_MAP} -v ${LOCAL_VOLUME_DIR}/$vol:$vol"
        else
            # -- default sub-directory (without prefix absolute path) --
            VOLUME_MAP="${VOLUME_MAP} -v ${LOCAL_VOLUME_DIR}/$vol:${DOCKER_VOLUME_DIR}/$vol"
        fi
        mkdir -p ${LOCAL_VOLUME_DIR}/$vol
        ls -al ${LOCAL_VOLUME_DIR}/$vol
    done
}
#### ---- Generate Volumes Mapping ----
generateVolumeMapping
echo ${VOLUME_MAP}

###################################################
#### ---- Mostly, you don't need change below ----
###################################################

#instanceName=my-${1:-${imageTag%/*}}_$RANDOM
#instanceName=my-${1:-${imageTag##*/}}
## -- transform '-' and space to '_' 
instanceName=`echo $(basename ${imageTag})|tr '[:upper:]' '[:lower:]'|tr "/\-: " "_"`

echo "---------------------------------------------"
echo "---- Starting a Container for ${imageTag}"
echo "---------------------------------------------"
DISPLAY=${MY_IP}:0 \
docker run -ti --rm \
    --name=${instanceName} \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    ${VOLUME_MAP} \
    ${imageTag}


