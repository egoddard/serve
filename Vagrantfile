# -*- mode: ruby -*-
# vi: set ft=ruby;

VB_NAME = serve
CPUS = 2
MEMORY = 2048

Vagrant.configure(2) do |config|
    config.vm.box = "ubuntu/trusty64"
    config.vm.hostname = VB_NAME
    config.vm.host_name = VB_NAME

    config.vm.provider "virtualbox" do |vb|
        vb.memory = MEMORY
        vb.cpus = CPUS
        vb.name = VB_NAME
    end

    config.vm.provision "shell", privileged: true, path: "install.sh"
end

