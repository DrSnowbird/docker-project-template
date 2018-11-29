#!/bin/bash

set -e

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
    exec "/bin/bash";
else
    exec "$@";
fi
