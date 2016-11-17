#!/bin/bash

# Install the required packages
apt-get update
apt-get install -y git nginx python-pip python-virtualenv pcregrep

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

# Make folder to hold app nginx configs
if [ ! -d '/etc/nginx/apps.d' ]; then
    mkdir /etc/nginx/apps.d
    chown serve:serve /etc/nginx/apps.d
fi

# Make folder to hold app repos
if [ ! -d '/opt/serve' ]; then
    mkdir /opt/serve
    chown serve:serve /opt/serve
fi

# Make sure ssh folder and authorized keys exist
mkdir -p /home/serve/.ssh

if [ ! -e /home/serve/.ssh/authorized_keys ]; then
    touch /home/serve/.ssh/authorized_keys
fi

chown -R serve:serve /home/serve/.ssh
chmod 700 /home/serve/.ssh

# Delete existing installation
if [ -d '/home/serve/serve' ]; then
    echo "Removing existing installation..."
    sudo -u serve -H sh -c "rm -rf /home/serve/serve/"
fi

# Copy the serve folder to the serve users's home directory and fix permissions
if [ -d '/vagrant' ]; then
    echo "In a vagrant vm, switching to shared directory..."
    cd /vagrant
fi

echo "Copying the Serve app to the serve user's folder..."
mkdir -p /home/serve/serve
cp -r . /home/serve/serve
chown -R serve:serve /home/serve/serve


# Create a virtualenv to install the commands into
echo "Creating the Python virtual environment..."
sudo -u serve -H sh -c "virtualenv /home/serve/serve/.venv"

echo "Activating the virtual environment..."
echo `pwd`
echo `ls`
sudo -u serve -H sh -c "cd /home/serve/serve; . .venv/bin/activate; python setup.py install"

echo "Adding serve command to path..."
sudo -u serve -H sh -c "mkdir -p /home/serve/bin"

if [ ! -h '/home/serve/bin/serve' ]; then
    sudo -u serve -H sh -c "ln -s /home/serve/serve/.venv/bin/serve /home/serve/bin/serve"
fi

# Add serve to sudoers with permission to reload nginx
echo "serve ALL = NOPASSWD: /etc/init.d/nginx reload,/etc/init.d/nginx start, /etc/init.d/nginx stop" >> /etc/sudoers

# Replace default nginx configuration
cp serve_nginx_default.conf /etc/nginx/sites-available/default

# Create the local apps directory
mkdir -p /home/serve/apps

# Copy the bashrc script so the serve user has a reasonable bash prompt with completion
cp .bashrc /home/serve/.bashrc
chown serve:serve /home/serve/.bashrc

echo "Finished installing Serve."
echo "Restart the server to make sure the serve user has the correct permissions."
