#!/bin/bash

set -e

# Set options for uvcvideo kernel module
echo "options uvcvideo nodrop=1 timeout=5000 quirks=0x80" > /etc/modprobe.d/uvcvideo.conf

# Install X server and utils
apt-get update
apt-get install --yes xinit x11-xserver-utils \
    ntp usbutils htop \
    fswebcam \
    gstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad
sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

# Install app dependencies
apt-get install --yes python-pip python-dev \
    python-qt4 python-dbus python-zbar \
    bluez libbluetooth-dev libusb-0.1-4 libusb-1.0-0 \
    libssl-dev libjpeg-dev libffi-dev
ln -s /bin/hciconfig /usr/sbin/hciconfig

# Install salt and generate device key
apt-get install --yes salt-minion
echo "master: sam.xbthq.co.uk" > /etc/salt/minion.d/master.conf
sha256sum /etc/machine-id | cut -d" " -f1 > /etc/salt/minion_id
systemctl restart salt-minion

# Install packages from PyPI
pip install pip setuptools --upgrade
su - vagrant -c "pip install -r /vagrant/requirements.txt --user"
