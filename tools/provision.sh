#!/bin/bash

# Set options for uvcvideo kernel module
echo "options uvcvideo nodrop=1 timeout=5000 quirks=0x80" > /etc/modprobe.d/uvcvideo.conf

# Install X server and utils
apt-get update
apt-get install --yes xinit x11-xserver-utils ntp usbutils htop fswebcam
sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

# Install app dependencies
apt-get install --yes python-pip python-dev python-qt4 libbluetooth-dev bluez python-dbus libusb-0.1-4 libusb-1.0-0 libjpeg-dev libffi-dev python-opencv python-zbar
ln -s /usr/sbin/hciconfig /usr/bin/hciconfig
pip install -r /vagrant/requirements.txt

# Install nfcpy
wget --quiet https://launchpad.net/nfcpy/0.10/0.10.0/+download/nfcpy-0.10.0.tar.gz
tar -xzf nfcpy-0.10.0.tar.gz
cp -r 0.10.0/nfc /usr/local/lib/python2.7/dist-packages/
rm -rf 0.10.0 nfcpy-0.10.0.tar.gz
