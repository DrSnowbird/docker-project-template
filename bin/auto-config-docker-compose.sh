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

# Current directory as base for additional child directories to be mapped into Container
DOCKER_COMPOSE_TEMPLATE="${PROJ_DIR}/docker-compose.yml.template"
echo

if [ ! -s ${DOCKER_COMPOSE_TEMPLATE} ]; then
    echo "*** WARNING ***: Can't find ${DOCKER_COMPOSE_TEMPLATE} template file! Ignore creation local volumes dir!"
else
    #volumes="./app ./data ./workspace ./.vscode/extensions"
    # cat docker-compose.yml.template |grep -E '^( |\t)*- .\/.*:.*$'|cut -d':' -f1|awk '{print $2}'
    volumes_current_dir="`cat ${DOCKER_COMPOSE_TEMPLATE} |grep -E '^( |\t)*- +.\/.*:.*$'|cut -d':' -f1|awk '{print $2}' ` "
    for v in $volumes_current_dir; do
        if [ ! -s $v ]; then
            mkdir -p ${PROJ_DIR}/$v
        fi
    done
fi
