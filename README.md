# README

## Requirements

* Python 2
* VirtualBox
* Oracle VirtualBox Extension Pack
* Vagrant

## Running VM

Specify batch number in `xbterminal/runtime/batch_number` file.

Write device key to `xbterminal/runtime/device_key` file.

Put these options in `xbterminal/runtime/local_config`:

```
{
  "use_dev_remote_server": true,
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

## Versioning

To add a new version:

1. Update [VERSION](VERSION) file.
2. Commit changes.
3. Set tag: `git tag -a v0.9.4` ([more info](https://git-scm.com/book/en/v2/Git-Basics-Tagging)).

## Compiling

Requirements:

* Fabric
* QEMU

### Remote server

```
fab build.remote_compile
```

This command outputs two files:

* Binary executable `build/main_{version}_{arch}`
* Installation package `build/xbterminal-firmware_{version}_{arch}.tar.gz`.

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

