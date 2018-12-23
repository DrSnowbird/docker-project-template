#!/bin/bash

set -e

#### ---- Make sure to provide Non-root user for launching Docker ----
#### ---- Default, we use base images's "developer"               ----
NON_ROOT_USER=${1:-"${USER_NAME}"}
NON_ROOT_USER=${NON_ROOT_USER:-"developer"}

#### ------------------------------------------------------------------------
#### ---- You need to set PRODUCT_EXE as the full-path executable binary ----
#### ------------------------------------------------------------------------
echo "Starting docker process daemon ..."
/bin/bash -c "${EXE_COMMAND:-echo Hello}"

#### ------------------------------------------------------------------------
#### ---- Extra line added in the script to run all command line arguments
#### ---- To keep the docker process staying alive if needed.
#### ------------------------------------------------------------------------

#### **** Change this to your command pattern **** ####
EXE_PATTERN="/bin/bash"

#### **** Start processing command **** ####
if [ $# -lt 1 ]; then
    exec "/bin/bash"
else
    # check for the expected command
    if [[ "$1" =~ "$EXE_PATTERN" ]]; then
        #### 0.) Setup needed stuffs, e.g., init db etc. ....
        #### (do something here for preparation if any)
    
        #### **** Allow non-root users to bind to use lower than 1000 ports **** ####
        USE_CAP_NET_BIND=${USE_CAP_NET_BIND:-0}
        if [ ${USE_CAP_NET_BIND} -gt 0 ]; then
            sudo setcap 'cap_net_bind_service=+ep' ${EXE_COMMAND}
        fi

        #### 1.) Setup needed stuffs, e.g., init db etc. ....
        #### (do something here for preparation)
        
        #### 2.A) As Root User -- Choose this or 2.B --####
        #### ---- Use this when running Root user ---- ####
        #exec ${EXE_COMMAND} "$@"
        
        #### 2.B) As Root User -- Choose this or 2.A  ---- #### 
        #### ---- Use this when running Non-Root user ---- ####
        #### ---- Use gosu (or su-exec) to drop to a non-root user
        exec gosu ${NON_ROOT_USER} ${EXE_COMMAND} "$@"
    fi
fi
# Default to run whatever the user wanted like "bash" or "sh"
exec "$@"
