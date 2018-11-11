#!/bin/bash

set -e

echo "Starting docker process daemon ..."
#### ------------------------------------------------------------------------
#### ---- You need to set PRODUCT_EXE as the full-path executable binary ----
#### ------------------------------------------------------------------------
/bin/bash -c "${PRODUCT_EXE:-echo Hello}"

#Extra line added in the script to run all command line arguments
if [ $# -lt 1 ]; then
    exec "/bin/bash";
else
    exec "$@";
fi
