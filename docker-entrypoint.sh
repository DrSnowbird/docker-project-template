#!/bin/bash
#
###########################################################################
#### ---- docker-entrypoint.sh: for application with ./app folder ---- ####
###########################################################################

# docker-entrypoint.sh
#
# The Dockerfile CMD, or any "docker run" command option, gets
# passed as command-line arguments to this script.

# Abort on any error (good shell hygiene)
set -e

env

APP_MAIN=${APP_MAIN:-setup.sh}

base_app=$(basename $APP_MAIN)
find_app_main=`find $HOME -name $base_app -print | head -n 1`
if [ "${find_app_main}" != "" ]; then
    APP_MAIN=${find_app_main}
    echo "--- Found the actual location of APP_MAIN: ${APP_MAIN}"
    # If we're running "myAppName", provide default options
    if [ "$(basename $1)" = "$(basename $APP_MAIN)" ]; then
        echo ">> Running: ${APP_MAIN}"
        shift 1
        # Then run it with default options plus whatever else
        # was given in the command
        exec ${APP_MAIN} $@
        tail -f /dev/null
    else
       # Otherwise just run what was given in the command
       echo ">> Running: $@"
       $@
    fi
else
    echo "--- APP_MAIN not found in CMD (from Dockerfile or run) ..."
    $@
fi

