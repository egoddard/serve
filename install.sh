#!/bin/bash

# Install the required packages
apt-get update
apt-get install -y git nginx

apt-get install -y apt-transport-https ca-certificates
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

# Install docker and its dependencies
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update

apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual
apt-get install -y docker-engine

# Start docker and set it to start on boot
service docker start
systemctl enable docker

# Configure the Docker group so that docker commands can be run without root permission
groupadd docker

useradd -m -G docker serve
