#!/bin/bash

set -e

#### ---- Make sure to provide Non-root user for launching Docker ----
#### ---- Default, we use base images's "developer"               ----
NON_ROOT_USER=${1:-"${USER_NAME}"}
NON_ROOT_USER=${NON_ROOT_USER:-"developer"}

echo "Starting docker process daemon ..."
#### ------------------------------------------------------------------------
#### ---- You need to set PRODUCT_EXE as the full-path executable binary ----
#### ------------------------------------------------------------------------
/bin/bash -c "${EXE_COMMAND:-echo Hello}"

#### ------------------------------------------------------------------------
#### ---- Extra line added in the script to run all command line arguments
#### ---- To keep the docker process staying alive if needed.
#### ------------------------------------------------------------------------
if [ $# -lt 1 ]; then
    exec "/bin/bash"
else
    # check for the expected command
    if [ "$1" = 'mongod' ]; then
        # Setup needed stuffs, e.g., init db etc. ....
        # Use gosu (or su-exec) to drop to a non-root user
        exec gosu ${NON_ROOT_USER} "$@"
    fi
fi
# Default to run whatever the user wanted like "bash" or "sh"
exec "$@"

