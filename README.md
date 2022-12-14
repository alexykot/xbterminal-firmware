# README

## Requirements

* Python 2
* pyqt4-dev-tools
* libbluetooth-dev
* Fabric
* VirtualBox
* Oracle VirtualBox Extension Pack
* Vagrant

## Running VM

Generate ui and resource modules:

```
fab build
```

Specify batch number in `xbterminal/runtime/batch_number` file.

Put these options in `xbterminal/runtime/local_config`:

```
{
  "remote_server": "stage",
  "show_cursor": true
}
```

Create the VM and run it:

```
vagrant up
```

Attach a webcam to the running VM ([more info](http://www.virtualbox.org/manual/ch09.html#idp99569632)):

```
VBoxManage controlvm "XBTerminal Device" webcam attach /dev/video0
```

Login to the VM:

```
vagrant ssh
```

Get new device key:

```
cp /etc/salt/minion_id /vagrant/xbterminal/runtime/device_key
```

#### GUI application

Start the application and activate device at http://stage.xbterminal.com:

```
xinit /vagrant/xbterminal/main.py
```

#### JSON-RPC server

Start server:

```
python /vagrant/xbterminal/main_rpc.py
```

JSON-RPC server accepts connections on port **8888**.

## Versioning

To add a new version:

1. Execute `fab build.version:patch`. Command argument can also be `major` or `minor`.
2. Push changes to repo `git push origin --tags` ([more info](https://git-scm.com/book/en/v2/Git-Basics-Tagging)).

## Compiling

Requirements:

* Fabric
* QEMU

### Remote server

```
fab build.remote_compile
```

This command outputs two files:

* Binary executables `build/main_{version}_{arch}` and `build/main_rpc_{version}_{arch}`.
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
* SSH port: **32522** (*at localhost*).

More info can be found here: https://people.debian.org/~aurel32/qemu/armhf/README.txt

Wait until VM is ready, then start the compilation:

```
fab build.qemu_compile
```

## GUI

**QtDesigner** is required.

After editing UI file (*.ui), recompile it:

```
fab build.qt_ui
```

## Translations

[Qt Linguist](http://doc.qt.io/qt-4.8/linguist-manual.html) is required.

Update translation files (*.ts):

```
fab build.qt_translations
```

Then run Qt Linguist. All translation files can be opened in one window.

After finishing translations, select **File > Release All** from the main menu.
