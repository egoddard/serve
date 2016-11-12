#!/bin/bash

# Install the required packages
apt-get update
apt-get install -y git nginx python-pip python-virtualenv

apt-get install -y apt-transport-https ca-certificates
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

# Install docker and its dependencies
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update

apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual
apt-get install -y docker-engine

# Start docker and set it to start on boot
service docker start

useradd -m -G docker serve

# Copy the serve folder to the serve users's home directory and fix permissions
echo "Copying the Serve app to the serve user's folder..."
cp -r . /home/serve/serve
chown -R serve:serve /home/serve/serve

# Create a virtualenv to install the commands into
echo "Creating the Python virtual environment..."
sudo -u serve -H sh -c "virtualenv /home/serve/serve/.venv"

echo "Activating the virtual environment..."
sudo -u serve -H sh -c "cd /home/serve/serve; . .venv/bin/activate; python setup.py install"

echo "Adding serve command to path..."
sudo -u serve -H sh -c "mkdir -p /home/serve/bin"
sudo -u serve -H sh -c "ln -s /home/serve/serve/.venv/bin/serve /home/serve/bin/serve"

echo "Finished installing Serve."
echo "Restart the server to make sure the serve user has the correct permissions."
