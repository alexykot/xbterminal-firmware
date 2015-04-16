# README #

### Requirements ###

* Python 2
* Vagrant
* VirtualBox

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

Create VM and run main process:

```
vagrant up
vagrant ssh
xinit /vagrant/xbterminal/main.py
```
