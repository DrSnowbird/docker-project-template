#!/bin/bash -x

echo "... Starting subnet & gateway network named, iptastic ..."

docker network create --subnet 203.0.113.0/24 --gateway 203.0.113.254 iptastic
docker run --rm -it --net iptastic --ip 203.0.113.2 nginx

echo "... Use another terminal to run the folowing Client HTTP connect to Nginx"
echo "curl 203.0.113.2 "
