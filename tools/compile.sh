#!/bin/bash -x

# Compile application
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

# Compile themes
for THEME_MODULE in $(find xbterminal/gui/themes/*.py)
do
    nuitka \
        --python-version=2.7 \
        --clang \
        --recurse-none \
        --output-dir=build/themes \
        --show-progress \
        --module \
        $THEME_MODULE
done

# Collect files
mkdir -p build/pkg/xbterminal/runtime
mkdir -p build/pkg/xbterminal/gui/themes
mkdir -p build/pkg/xbterminal/gui/ts
cp LICENSE build/pkg/
cp build/main.exe build/pkg/xbterminal/main
cp build/themes/*.so build/pkg/xbterminal/gui/themes/
cp xbterminal/gui/ts/*.qm build/pkg/xbterminal/gui/ts/
