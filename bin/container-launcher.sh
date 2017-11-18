#!/bin/bash

echo "---------------------------- Usage -------------------------"
echo "$(basename $0) \"pattern_of_container_name\" "
echo "  e.g.: To launch mysql-5 container, do this: "
echo "    $(basename $0) \"sql.5\" "
echo
pattern=${1:-"scala-ide-docker"}

#### ---- Change this base dir to yours first for adjusting to your environment ----
container_root="$HOME/github-PUBLIC"
container_paths=`ls $container_root`
tools_paths="
blazegraph
Cassandra
docker-agraph
docker-deep-learning
docker-hadoop-spark-workbench
docker-rstudio
docker-spark-bde2020-zeppelin
eclipse-oxygen-docker
graphdb
gruff-with-allegrograph
jetty-fileserver
mysql-5
mysql-8
mysql-workbench
netbeans
openrefine
protege-docker-x11
scala-ide-docker
scikit-docker
tensorflow-python3-jupyter
"
if [ ! -d  $container_root ]; then
    echo "*** ERROR: container base dir $container_root not existing"
    exit 1
fi

echo "------------------------------------------------------------"
echo "  Warning: "
echo "    First container's folder-name matched to your pattern"
echo "    will be run first and launching done and exit."
echo "------------------------------------------------------------"
#for path in $tools_paths; do
for path in `ls $container_root` ; do
    found=`echo ${path} | grep -i -e "${pattern}"`
    if [ "$found" != "" ]; then
        if [ -e  $container_root/$path/run.sh ]; then
            cd $container_root/$found
            echo
            echo "-------------------------------------------------------------------------"
            echo "... Launching docker-based application: $found now ..."
            echo ">>> $container_root/$found/run.sh "
            $container_root/$found/run.sh
            echo "-------------------------------------------------------------------------"
            echo
            exit 0
        else
            echo "*** ERROR: container launcher script: $container_root/$found/run.sh file not found! ****"
        fi
    fi
done
