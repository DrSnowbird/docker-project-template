#!/bin/bash -x

# reference: https://docs.docker.com/engine/installation/linux/docker-ce/centos/#install-using-the-repository

docker-compose --version
docker --version

sudo yum remove docker docker-common docker-selinux docker-engine
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce

yum list docker-ce --showduplicates | sort -r

sudo systemctl start docker
sudo systemctl enable  docker

docker --version
docker-compose --version

