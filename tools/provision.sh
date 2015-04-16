#!/bin/bash

apt-get update
apt-get install --yes xinit x11-xserver-utils usbutils ntp
sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

# Install dependencies
apt-get install --yes python-pip python-dev python-qt4 libbluetooth-dev bluez python-dbus libusb-0.1-4 libusb-1.0-0 python-opencv python-zbar
ln -s /usr/sbin/hciconfig /usr/bin/hciconfig
pip install distribute --upgrade
pip install -r /vagrant/requirements.txt

# Install nfcpy
wget --quiet https://launchpad.net/nfcpy/0.9/0.9.2/+download/nfcpy-0.9.2.tar.gz
tar -xzf nfcpy-0.9.2.tar.gz
cp -r nfcpy-0.9.2/nfc /usr/local/lib/python2.7/dist-packages/
rm -rf nfcpy-0.9.2 nfcpy-0.9.2.tar.gz
