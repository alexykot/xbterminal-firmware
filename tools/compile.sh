#!/bin/bash

nuitka \
    --python-version=2.7 \
    --clang \
    --recurse-all \
    --recurse-not-to=PyQt4 \
    --recurse-not-to=requests \
    --recurse-not-to=bluetooth \
    --recurse-not-to=dbus \
    --recurse-not-to=google \
    --recurse-not-to=cv2 \
    --recurse-not-to=ntplib \
    --recurse-not-to=cryptography \
    --recurse-not-to=nfc \
    --recurse-not-to=qrcode \
    --recurse-not-to=zbar \
    --recurse-not-to=PIL \
    --recurse-not-to=wifi \
    --recurse-not-to=Adafruit_BBIO \
    --recurse-not-to=usb \
    --recurse-not-to=psutil \
    --output-dir=build \
    --show-progress \
    --show-modules \
    xbterminal/main.py
