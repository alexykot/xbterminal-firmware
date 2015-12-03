Vagrant.configure(2) do |config|
  config.vm.box = "debian/jessie64"
  config.vm.hostname = "xbterminal-vm"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "XBTerminal"
    vb.gui = true
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbehci", "on"]
  end

  config.vm.provision "shell", path: "tools/provision.sh"
end
