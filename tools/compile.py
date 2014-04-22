#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import subprocess


subprocess.check_call(['nuitka',
                      '--python-version=2.7',
                      '--recurse-directory=/opt/xbterminal',
                      '--output-dir=/opt/xbterminal/compiled/',
                      '--remove-output',
                      '--warn-implicit-exceptions',
                      '--unstripped',
                      # '--show-scons',
                      # '--show-progress',
                      # '--show-modules',

                      # '--recurse-all',
                      '--recurse-to=xbterminal',
                      '--recurse-to=exceptions',
                      '--recurse-to=helpers',
                      '--recurse-to=instantfiat',
                      '--recurse-to=defaults',
                      '--recurse-to=blockchain',
                      '--recurse-to=bitcoinaverage',
                      '--recurse-to=keypad',
                      '--recurse-to=gui',

                      '--recurse-not-to=PyQt4',
                      '--recurse-not-to=bitcoinrpc',
                      '--recurse-not-to=bitcoinrpc.connection',
                      '--recurse-not-to=requests',
                      '--recurse-not-to=qrcode',
                      '--recurse-not-to=wifi',
                      '--recurse-not-to=nfc',
                      '--recurse-not-to=nfc.snep',
                      '--recurse-not-to=eventlet.green',
                      '--recurse-not-to=eventlet.timeout',
                      '--recurse-not-to=simplejson',
                      '--recurse-not-to=Adafruit_BBIO',

                      '/opt/xbterminal/xbterminal/main.py'],
                      cwd='/opt/xbterminal/')
