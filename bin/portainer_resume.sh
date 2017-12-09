#!/bin/bash 

# This feature is not yet available for native Docker Windows containers.
# On Linux and when using Docker for Mac or Docker for Windows or 
# Docker Toolbox, 
# ensure that you have started Portainer container with the following 
# Docker flag 
#    -v "/var/run/docker.sock:/var/run/docker.sock"

TO_REUSE=1

MY_IP=`ip route get 1|awk '{print$NF;exit;}'`

#ref: http://portainer.io/install.html
#ref: https://portainer.readthedocs.io/en/stable/deployment.html#quick-start

if [ $# -le 1 ]; then
    echo "Usage: $0 [<remote-host>:default localhost] [<windows_host>]"
    echo "e.g"
    echo "localhost docker management:"
    echo "$0"
    echo "Remote Unix docker management:"
    echo "$0 192.168.0.206"
    echo "Remote Windows docker management:"
    echo "$0 192.168.0.206 windows"
    echo "---------------------------------"
fi

remote_host=${1}
remote_windows=${2}

#######################################################
#### ---- Change this base port number as you like ----
#######################################################
port_base=19000
port_use=9000

#######################################################
#######################################################
#### ---- Mostly, you don't want to change below:  ----
#######################################################
#######################################################

displayPortainerURL() {
    port=${1:-$port_base}
    echo "... Go to: http://${MY_IP}:${port}"
    #firefox http://${MY_IP}:${port} &
    if [ "`which google-chrome`" != "" ]; then 
        /usr/bin/google-chrome http://${MY_IP}:${port} &
    else
        firefox http://${MY_IP}:${port} &
    fi

}

#### ---- clean up old/dead Portainer containers ----
function cleanupOld() {
    #old_to_clean="`docker ps|grep portainer|grep "Exit"|awk '{print $1}'`"
    old_to_clean="`docker ps -a|grep portainer|awk '{print $1}'`"
    if [ "$old_to_clean" != "" ]; then
        for old in $old_to_clean; do
            docker rm -f $old
        done
    fi
}

function reuseOld() {
    oldToReuse="`docker ps -a|grep portainer|grep 'Exit'|awk '{print $1}'`"
    if  [ "$oldToReuse" != "" ]; then
        echo ">> Reuse old Portainer by restarting ... $oldToReuse"
        docker start $oldToReuse
    else
        alreadyRunning="`docker ps -a|grep portainer|grep -v 'Exit'|awk '{print $1}'`"
        if  [ "$alreadyRunning" != "" ]; then
            echo ">> Portainer docker already running: ... $alreadyRunning" 
        else
            echo "... Need to create a new one since non-existing! ..."
            TO_REUSE=0
        fi
    fi
}
if [ $TO_REUSE -eq 1 ]; then
    reuseOld
    if [ $TO_REUSE -eq 1 ]; then
        echo "... Reuse is done ..."
        displayPortainerURL
        exit 0
    fi
else
    echo cleanupOld
fi

#### ---- Find available Portainer containers ----
function findNextPort() {
    ports_occupied=`docker ps -a |grep portainer|grep -v "Exit"|cut -d':' -f2|cut -d'-' -f1 | sort -u`
    echo "... Min. base port: $port_base"
    max=$port_base
    for v in $ports_occupied; do
        if (( $v > $max )); then max=$v; fi; 
    done
    port_use=$((max++))
    echo "port_use=$port_use"
}
findNextPort

if [ "$remote_host" == "" ]; then
    # Manage local Linux host
    # It's necessary to "bind" to docker.sock now:
    docker run --rm -d --privileged --name "portainer" -p ${port_use}:9000 -v /var/run/docker.sock:/var/run/docker.sock -v $HOME/portainer:/data portainer/portainer
else
    if [ "$remote_windows" == "" ]; then
        # Manage remote Linux host
        docker run -d --name "portainer" -p ${port_use}:9000 portainer/portainer -H tcp://${remote_host}:2375
    else
        # Manage remote Window host
        docker run -d --name "portainer" -p ${port_use}:9000 portainer/portainer:windows -H tcp://${remote_host}:2375
    fi
fi
displayPortainerURL ${port_use}

