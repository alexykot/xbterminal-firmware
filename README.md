# README

## Requirements

* Python 2
* VirtualBox
* Oracle VirtualBox Extension Pack
* Vagrant

## Running VM

Put these options in `xbterminal/runtime/local_state`:

```
{
  "use_default_keypad_override": true,
  "use_dev_remote_server": true,
  "use_predefined_connection": true,
  "show_cursor": true
}
```

Create the VM and run it:

```
vagrant up
```

Attach a webcam to the running VM ([more info](http://www.virtualbox.org/manual/ch09.html#idp99569632)):

```
VBoxManage controlvm "XBTerminal" webcam attach /dev/video0
```

Start the main process:

```
vagrant ssh
xinit /vagrant/xbterminal/main.py
```

## Compiling

Requirements:

* Fabric
* QEMU

### Remote server

```
fab build.remote_compile
```

This command outputs two files:

* Binary executable `build/main_{arch}_{version}`
* Installation package `build/xbterminal-firmware_{arch}_{version}.tar.gz`.

### QEMU VM

Create and run VM:

```
fab build.qemu_start:arch=armhf
```

This command downloads necessary files and starts QEMU in daemonized mode.

* Root password: **root**
* User account: **user**
* User password: **user**
* SSH port: **32522** (*@localhost*).

More info can be found here: https://people.debian.org/~aurel32/qemu/armhf/README.txt

Wait until VM is ready, then start the compilation:

```
fab build.qemu_compile
```
