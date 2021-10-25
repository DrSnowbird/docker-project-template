#!/bin/bash -x
#
# docker-entrypoint.sh
#
# The Dockerfile CMD, or any "docker run" command option, gets
# passed as command-line arguments to this script.

# Abort on any error (good shell hygiene)
set -e

env
whoami
env | sort

echo "Inputs: $*"


#### ------------------------------------------------------------------------
#### ---- Extra line added in the script to run all command line arguments
#### ---- To keep the docker process staying alive if needed.
#### ------------------------------------------------------------------------
set -v
if [ $# -gt 0 ]; then

    #### 1.) Setup needed stuffs, e.g., init db etc. ....
    #### (do something here for preparation)
    exec "$@"

else
    /bin/bash
fi

#tail -f /dev/null
