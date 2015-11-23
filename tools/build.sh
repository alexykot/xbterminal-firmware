#!/bin/bash -x

# Build ui module
pyuic4 xbterminal/gui/ui.ui -o xbterminal/gui/ui.py

# Build theme modules
for THEME_DIR in $(find xbterminal/gui/themes/* -maxdepth 0 -type d)
do
    THEME_NAME=`basename $THEME_DIR`
    pyrcc4 $THEME_DIR/resources.qrc -o xbterminal/gui/themes/$THEME_NAME.py
done
