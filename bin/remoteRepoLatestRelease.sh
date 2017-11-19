#!/bin/bash 

#### ---- Install: docker-compose ----
org=${1:-docker}
repo=${2:-compose}

#sudo yum install jq net-tools -y

release=`curl https://api.github.com/repos/$org/$repo/releases/latest -s | jq .name -r`

echo ${release}
