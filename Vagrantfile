Vagrant.configure("2") do |config|
  # Specify base box
  config.vm.box = "ubuntu/trusty64"

  # Execute bootstrap script
  config.vm.provision :shell, path: "bootstrap.sh", privileged: false

  # Configure port forwarding
  config.vm.network :forwarded_port, guest: 8000, host: 1337

  # Virtualbox configuration
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end
end
