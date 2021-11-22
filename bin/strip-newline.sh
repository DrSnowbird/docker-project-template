#!/bin/bash -x

if [ $# -lt 1 ]; then
    echo "*** ERROR: need provide file/directory to concatenate multiple lines into one line"
    exit 1
fi

FileToStrip=${1}

for f in `ls ${FileToStrip}` ; do
    cp $f $f.bak
    # awk '{printf("%s",$0)}'
    sed -e '/^$/d' $f | tr '\n' ' ' | tee $f
done
