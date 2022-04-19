CPU = 1
MEMORY = 2048
IP_ADDRESS = "192.168.56.11"


Vagrant.configure("2") do |config|
    config.vm.define "djangoServer" do |django|
        django.vm.box = "hashicorp/bionic64"
        django.vm.network "private_network", ip: "#{IP_ADDRESS}"
        django.vm.hostname = "djangoServer"
        django.vm.provider "virtualbox" do |v|
            v.memory = MEMORY
            v.cpus = CPU
        end
    end
end
