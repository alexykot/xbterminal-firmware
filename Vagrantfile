Vagrant.configure(2) do |config|
  config.vm.box = "chef/debian-7.8"
  config.vm.hostname = "xbterminal-vm"
  config.ssh.username = "vagrant"
  config.ssh.password = "vagrant"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "XBTerminal"
    vb.gui = true
    vb.customize ["modifyvm", :id, "--usb", "on"]
  end

  config.vm.provision "shell", path: "tools/provision.sh"
end
