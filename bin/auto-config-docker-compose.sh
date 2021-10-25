#!/bin/bash -x

################################ Usage #######################################

## ---------- ##
## -- main -- ##
## ---------- ##

#set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PROJ_DIR=$(dirname $DIR)

cd ${PROJ_DIR}

bin/auto-config-with-template.sh $@ docker-compose.yml.template

###################################################
#### ---- Detect Docker Run Env files ----
###################################################
## -- (this script will include ./.env only if "./docker-run.env" not found
DOCKER_ENV_FILE="${PROJ_DIR}/.env"
function detectDockerRunEnvFile() {
    curr_dir=`pwd`
    if [ -s "./.env" ]; then
        echo "--- INFO: ./.env FOUND to use as Docker Run Environment file!"
        DOCKER_ENV_FILE="./.env"
    else
        echo "--- INFO: ./.env Docker Environment file (.env) NOT found!"
        if [ -s "./docker.env" ]; then
            echo "--- INFO: ./docker.env FOUND to use as Docker Run Environment file!"
            DOCKER_ENV_FILE="./docker.env"
        else
            echo "*** WARNING: Docker Environment file (.env) or (docker.env) NOT found!"
        fi
    fi

}
detectDockerRunEnvFile

###################################################
#### ---- Function: Find Host IP  ----
####      (Don't change!)
###################################################
SED_MAC_FIX="''"
function find_host_ip() {
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        # ...
        HOST_IP=`ip route get 1|grep via | awk '{print $7}'`
        SED_MAC_FIX=
        echo ${HOST_IP}
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Mac OSX
        HOST_IP=`ifconfig | grep "inet " | grep -Fv 127.0.0.1 | grep -Fv 192.168 | awk '{print $2}'`
        CP_OPTION=
        echo ${HOST_IP}
    fi
}
find_host_ip

#######################################################
#### ---- Function: docker-compose: port mappings  ----
####      (Don't change!)
#######################################################
DOCKER_COMPOSE_FILE="${PROJ_DIR}/docker-compose.yml"
#{{PORTS_MAPPING}}
PORTS_MAPPING=""
prefix_yaml="\n      - "
function generatePortMapping_dockercompose() {
    if [ "$PORTS" == "" ]; then
        ## -- If locally defined in this file, then respect that first.
        ## -- Otherwise, go lookup the ${DOCKER_ENV_FILE} as ride-along source for volume definitions
        PORTS_LIST=`cat ${DOCKER_ENV_FILE}|grep "^#PORTS_LIST= *"|sed "s/[#\"]//g"|cut -d'=' -f2-`
    fi
    for pp in ${PORTS_LIST}; do
        #echo "$pp"
        port_pair=`echo $pp |  tr -d ' ' `
        if [ ! "$port_pair" == "" ]; then
            # -p ${local_dockerPort1}:${dockerPort1} 
            host_port=`echo $port_pair | tr -d ' ' | cut -d':' -f1`
            docker_port=`echo $port_pair | tr -d ' ' | cut -d':' -f2`
            PORTS_MAPPING="${PORTS_MAPPING}${prefix_yaml}\"${host_port}:${docker_port}\""
        fi
    done
    if [ "${PORTS_MAPPING}" != "" ]; then
        PORTS_MAPPING="    ports:${PORTS_MAPPING}\n"
    fi
}
#### ---- Generate Port Mapping ----
generatePortMapping_dockercompose
echo -e "PORT_MAP=\n${PORTS_MAPPING}"
sed -i ${SED_MAC_FIX} "s%^.*\#{{PORTS_MAPPING}}%$PORTS_MAPPING%g" ${DOCKER_COMPOSE_FILE}


###########################################################
#### ---- Function: docker-compose: volumes mappings  ----
####      (Don't change!)
###########################################################

function cutomizedVolume() {
    DATA_VOLUME=$1 
    if [ "`echo $DATA_VOLUME|grep 'volume-'`" != "" ]; then
        docker_volume=`echo $DATA_VOLUME | cut -d'-' -f2 | cut -d':' -f1`
        dest_volume=`echo $DATA_VOLUME | cut -d'-' -f2 | cut -d':' -f2`
        source_volume=$(basename $imageTag)_${docker_volume}
        sudo docker volume create ${source_volume}
        
        VOLUME_MAP="-v ${source_volume}:${dest_volume} ${VOLUME_MAP}"
    else
        echo "---- ${DATA_VOLUME} already is defined! Hence, ignore setup ${DATA_VOLUME} ..."
        echo "---> VOLUME_MAP=${VOLUME_MAP}"
    fi
}

EXCEPTION_SYS_DIR="/dev/shm /dev/snd /etc/hosts /var/run/docker.sock /tmp/.X11-unix"
function checkHostVolumePath() {
    _left=$1
    if [ ! -s ${_left} ]; then
        if [[ ! "${EXCEPTION_SYS_DIR}" =~ .*${_left}.* ]]; then
            mkdir -p ${_left}
            sudo chown -R $USER:$USER ${_left}
            if [ -s ${_left} ]; then 
                ls -al ${_left}
            else 
                echo "*** ERROR: ${_left}: Not existing!"
            fi
        fi
    fi
}

###################################################
#### **** Container Package information ****
###################################################

DOCKER_IMAGE_REPO=`echo $(basename $PWD)|tr '[:upper:]' '[:lower:]'|tr "/: " "_" `
imageTag="${ORGANIZATION}/${DOCKER_IMAGE_REPO}"
#PACKAGE=`echo ${imageTag##*/}|tr "/\-: " "_"`
PACKAGE="${imageTag##*/}"

###################################################
#### **** Container Volume Mapping information ****
###################################################
volmap_removed_sys_folders=""
function find_volumes_in_dockercompose() {
    volmap_removed_sys_folders=""
    _DOCKER_COMPOSE_FILE_=$1
    if [ ! -s ${_DOCKER_COMPOSE_FILE_} ]; then
        echo "*** WARNING ***: Can't find ${_DOCKER_COMPOSE_FILE_} template file! Ignore creation local volumes dir!"
    else
        #volumes="./app ./data ./workspace ./.vscode/extensions"
        # cat docker-compose.yml.template |grep -E '^( |\t)*- .\/.*:.*$'|cut -d':' -f1|awk '{print $2}'
        #volumes_current_dir="`cat ${_DOCKER_COMPOSE_FILE_} |grep -E '^( |\t)*- (\/|\.).*:.*$'|cut -d':' -f1' ` "
        volmap_existing="`cat ${_DOCKER_COMPOSE_FILE_} |grep -E '^( |\t)*- (\/|\.).*:.*$' | awk '{print $2}' `"
        echo -e "22===============>>>>\n\n volmap_existing = ${volmap_existing}"
        for vol in ${volmap_existing}; do
            echo "---> Volume: $vol"
            vol_left="`echo $vol |cut -d':' -f1 `"
            if [[ ! "${EXCEPTION_SYS_DIR}" =~ .*${vol_left}.* ]]; then
                volmap_removed_sys_folders="${volmap_removed_sys_folders} $vol"
            fi
        done
    fi
}
#find_volumes_in_dockercompose ${DOCKER_COMPOSE_FILE}

#### ---- Processing #{{MORE_VOLUMES_MAPPING}} : ---- ####
baseDataFolder="$HOME/data-docker"
LOCAL_VOLUME_DIR="${baseDataFolder}/${PACKAGE}"
## -- Container's internal Volume base DIR
DOCKER_VOLUME_DIR="/home/developer"
DOCKER_COMPOSE_FILE="${PROJ_DIR}/docker-compose.yml"
#{{VOLUMES_MAPPING}}
VOLUMES_MAPPING=""
VOLUMES_MAPPING_LIST=""
prefix_yaml="      - "
function generateVolumeMapping_dockercompose() {
    if [ "$VOLUMES_LIST" == "" ]; then
        ## -- If locally defined in this file, then respect that first.
        ## -- Otherwise, go lookup the docker.env as ride-along source for volume definitions
        VOLUMES_LIST=`cat ${DOCKER_ENV_FILE}|grep "^#VOLUMES_LIST= *"|sed "s/[#\"]//g"|cut -d'=' -f2-`
    fi
    echo -e "\n>>>> VOLUMES_LIST: $VOLUMES_LIST \n"
    
    for vol in $VOLUMES_LIST; do
        echo
        echo ">>>>>>>>> $vol"
        hasColon=`echo $vol|grep ":"`
        ## -- allowing change local volume directories --
        if [ "$hasColon" != "" ]; then
            if [ "`echo $vol|grep 'volume-'`" != "" ]; then
                cutomizedVolume $vol
            else
                echo "************* hasColon=$hasColon"
                left=`echo $vol|cut -d':' -f1`
                right=`echo $vol|cut -d':' -f2`
                leftHasDot=`echo $left|grep "^\./"`
                if [ "$leftHasDot" != "" ]; then
                    ## has "./data" on the left
                    debug "******** A. Left HAS Dot pattern: leftHasDot=$leftHasDot"
                    if [[ ${right} == "/"* ]]; then
                        ## -- pattern like: "./data:/containerPath/data"
                        echo "******* A-1 -- pattern like ./data:/data --"
                        VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}`pwd`/${left#./}:${right}"
                        VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} `pwd`/${left#./}:${right}"
                    else
                        ## -- pattern like: "./data:data"
                        echo "******* A-2 -- pattern like ./data:data --"
                        VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}`pwd`/${left#./}:${DOCKER_VOLUME_DIR}/${right}"
                        VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} `pwd`/${left#./}:${DOCKER_VOLUME_DIR}/${right}"
                    fi
                    checkHostVolumePath "`pwd`/${left}"
                else
                    ## No "./data" on the left
                    debug "******** B. Left  No ./data on the left: leftHasDot=$leftHasDot"
                    leftHasAbsPath=`echo $left|grep "^/.*"`
                    if [ "$leftHasAbsPath" != "" ]; then
                        debug "******* B-1 ## Has pattern like /data on the left "
                        if [[ ${right} == "/"* ]]; then
                            ## -- pattern like: "/data:/containerPath/data"
                            echo "****** B-1-a pattern like /data:/containerPath/data --"
                            VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}${left}:${right}"
                            VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} ${left}:${right}"
                        else
                            ## -- pattern like: "/data:data"
                            echo "----- B-1-b pattern like /data:data --"
                            VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}${left}:${DOCKER_VOLUME_DIR}/${right}"
                            VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} ${left}:${DOCKER_VOLUME_DIR}/${right}"
                        fi
                        checkHostVolumePath "${left}"
                    else
                        debug "******* B-2 ## No pattern like /data on the left"
                        rightHasAbsPath=`echo $right|grep "^/.*"`
                        debug ">>>>>>>>>>>>> rightHasAbsPath=$rightHasAbsPath"
                        if [[ ${right} == "/"* ]]; then
                            echo "****** B-2-a pattern like: data:/containerPath/data"
                            debug "-- pattern like ./data:/data --"
                            VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}${LOCAL_VOLUME_DIR}/${left}:${right}"
                            VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} ${LOCAL_VOLUME_DIR}/${left}:${right}"
                        else
                            debug "****** B-2-b ## -- pattern like: data:data"
                            VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}${LOCAL_VOLUME_DIR}/${left}:${DOCKER_VOLUME_DIR}/${right}"
                            VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} ${LOCAL_VOLUME_DIR}/${left}:${DOCKER_VOLUME_DIR}/${right}"
                        fi
                        checkHostVolumePath "${left}"
                    fi
                    mkdir -p ${LOCAL_VOLUME_DIR}/${left}
                    #if [ $DEBUG -gt 0 ]; then ls -al ${LOCAL_VOLUME_DIR}/${left}; fi
                fi
            fi
        else
            ## -- pattern like: "data"
            debug "-- default sub-directory (without prefix absolute path) --"
            VOLUMES_MAPPING="${VOLUMES_MAPPING}${prefix_yaml}${LOCAL_VOLUME_DIR}/$vol:${DOCKER_VOLUME_DIR}/$vol"
            VOLUMES_MAPPING_LIST="${VOLUMES_MAPPING_LIST} ${LOCAL_VOLUME_DIR}/$vol:${DOCKER_VOLUME_DIR}/$vol"
            if [ ! -s ${LOCAL_VOLUME_DIR}/$vol ]; then
                mkdir -p ${LOCAL_VOLUME_DIR}/$vol
            fi
            if [ $DEBUG -gt 0 ]; then ls -al ${LOCAL_VOLUME_DIR}/$vol; fi
        fi       
        echo ">>> expanded VOLUMES_MAPPING: ${VOLUMES_MAPPING}"
    done
}
#### ---- Generate Volumes Mapping ----
generateVolumeMapping_dockercompose

echo -e "\n>>>>\n EXCEPTION_SYS_DIR=\n${EXCEPTION_SYS_DIR}"
volumes_map_exists_in_dockercompose="`cat ${DOCKER_COMPOSE_FILE} |grep -E '^( |\t)*- (\/|\.|\\\$HOME|\~).*:.*$' | awk '{print $2}' `"
echo -e "====>volumes_map_exists_in_dockercompose = ${volumes_map_exists_in_dockercompose}"
echo -e "====> VOLUMES_MAPPING_LIST:\n${VOLUMES_MAPPING_LIST}"
MORE_VOLUMES_MAPPING=""
function find_volumes_in_dockercompose() {
    _volmap_exists_with_expanded_home_dir="`eval echo ${volumes_map_exists_in_dockercompose}`"
    echo -e "---->_volmap_exists_with_expanded_home_dir:\n ${_volmap_exists_with_expanded_home_dir} "
    for volmap in $VOLUMES_MAPPING_LIST; do
        #echo -e "----> checking volmap existing in docker-compose.yml or not: $volmap"
        if [[ ! "${_volmap_exists_with_expanded_home_dir}" =~ .*${volmap}.* ]]; then
            MORE_VOLUMES_MAPPING="${MORE_VOLUMES_MAPPING}${prefix_yaml}${volmap}\n"
        fi
    done
}
find_volumes_in_dockercompose
echo -e "================>MORE_VOLUMES_MAPPING:$MORE_VOLUMES_MAPPING"
sed -i ${SED_MAC_FIX} "s%^.*\#{{MORE_VOLUMES_MAPPING}}%$MORE_VOLUMES_MAPPING%g" ${DOCKER_COMPOSE_FILE}


#### ---- Auto create base directories for docker-compose's "volumes:" mapping ---- ####
#### ---- Current directory as base for additional child directories to be mapped into Container
DOCKER_COMPOSE_TEMPLATE="${PROJ_DIR}/docker-compose.yml.template"
function auto_mkdir_for_dockercompose() {
    if [ ! -s ${DOCKER_COMPOSE_TEMPLATE} ]; then
        echo "*** WARNING ***: Can't find ${DOCKER_COMPOSE_TEMPLATE} template file! Ignore creation local volumes dir!"
    else
        #volumes="./app ./data ./workspace ./.vscode/extensions"
        # cat docker-compose.yml.template |grep -E '^( |\t)*- .\/.*:.*$'|cut -d':' -f1|awk '{print $2}'
        volumes_current_dir="`cat ${DOCKER_COMPOSE_TEMPLATE} |grep -E '^( |\t)*- +.\/.*:.*$'|cut -d':' -f1|awk '{print $2}' ` "
        echo -e ">>>> volumes_current_dir = $volumes_current_dir"
        for v in $volumes_current_dir; do
            if [ ! -s $v ]; then
                checkHostVolumePath "${PROJ_DIR}/$v"
                #mkdir -p ${PROJ_DIR}/$v
            fi
        done
    fi
}
#auto_mkdir_for_dockercompose



