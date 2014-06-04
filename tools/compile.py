#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import subprocess

#compile bootstrap
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
                      '--recurse-to=defaults',

                      '--recurse-not-to=stages',
                      '--recurse-not-to=watcher',
                      
                      '--recurse-not-to=PyQt4',
                      '--recurse-not-to=requests',
                      '--recurse-not-to=wifi',
                      '--recurse-not-to=nfc',
                      '--recurse-not-to=nfc.snep',
                      '--recurse-not-to=nfc.llcp',
                      '--recurse-not-to=qrcode',
                      '--recurse-not-to=simplejson',
                      '--recurse-not-to=eventlet.green',
                      '--recurse-not-to=eventlet.timeout',

                      # '--recurse-not-to=bitcoinrpc',
                      # '--recurse-not-to=bitcoinrpc.connection',
                      # '--recurse-not-to=Adafruit_BBIO',

                      '/opt/xbterminal/bootstrap.py'],
                      cwd='/opt/xbterminal/')

#compile main
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
                      '--recurse-to=stages',
                      '--recurse-to=watcher',

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
