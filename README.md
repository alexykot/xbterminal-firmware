# README #

### Requirements ###

* Python 2
* VirtualBox
* Oracle VirtualBox Extension Pack
* Vagrant

### Running VM ###

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
