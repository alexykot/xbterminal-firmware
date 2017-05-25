#!/bin/bash -x

# Compile application
nuitka \
    --python-version=2.7 \
    --clang \
    --recurse-all \
    --recurse-not-to=PyQt4 \
    --recurse-not-to=requests \
    --recurse-not-to=qrcode \
    --output-dir=build \
    --show-progress \
    --show-modules \
    xbterminal/main_gui.py

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

# Compile RPC server module
nuitka \
    --python-version=2.7 \
    --clang \
    --recurse-all \
    --recurse-not-to=requests \
    --recurse-not-to=bluetooth \
    --recurse-not-to=dbus \
    --recurse-not-to=google \
    --recurse-not-to=cv2 \
    --recurse-not-to=ntplib \
    --recurse-not-to=cryptography \
    --recurse-not-to=nfc \
    --recurse-not-to=zbar \
    --recurse-not-to=PIL \
    --recurse-not-to=usb \
    --recurse-not-to=psutil \
    --recurse-not-to=tornado \
    --recurse-not-to=jsonrpc \
    --output-dir=build \
    --show-progress \
    --show-modules \
    xbterminal/main_rpc.py

# Collect files
mkdir -p build/pkg/xbterminal/runtime
mkdir -p build/pkg/xbterminal/gui/themes
mkdir -p build/pkg/xbterminal/gui/ts
cp LICENSE build/pkg/
cp CHANGELOG.md build/pkg
cp build/main_gui.exe build/pkg/xbterminal/main_gui
cp build/main_rpc.exe build/pkg/xbterminal/main_rpc
cp build/themes/*.so build/pkg/xbterminal/gui/themes/
cp xbterminal/gui/ts/*.qm build/pkg/xbterminal/gui/ts/
