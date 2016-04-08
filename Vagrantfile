Vagrant.configure(2) do |config|
  config.vm.box = "debian/contrib-jessie64"
  config.vm.hostname = "xbt-device"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "XBTerminal Device"
    vb.gui = true
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbehci", "on"]
  end

  config.vm.provision "shell", path: "tools/provision.sh"
end
