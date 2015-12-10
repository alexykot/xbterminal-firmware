Vagrant.configure(2) do |config|
  config.vm.box = "debian/jessie64"
  config.vm.box_version = "8.2.2"
  config.vm.hostname = "xbt-vm"

  # Force vboxsf (debian/jessie64 uses rsync by default)
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"

  config.vbguest.auto_update = true  # Requires vagrant-vbguest plugin

  config.vm.provider "virtualbox" do |vb|
    vb.name = "XBTerminal"
    vb.gui = true
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbehci", "on"]
  end

  config.vm.provision "shell", path: "tools/provision.sh"
end
