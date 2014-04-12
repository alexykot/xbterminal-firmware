#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import subprocess


subprocess.check_call(['nuitka',
                      # '--recurse-all',
                      '--recurse-directory=/opt/xbterminal',
                      '--remove-output',
                      '--output-dir=/opt/xbterminal/compiled/',
                      '--warn-implicit-exceptions',
                      '--unstripped',
                      # '--show-scons',
                      # '--show-progress',
                      # '--show-modules',
                      '--python-version=2.7',
                      '--recurse-to=xbterminal',
                      '--recurse-to=xbterminal.exceptions',
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
                      '/opt/xbterminal/xbterminal/main.py'],
                      cwd='/opt/xbterminal/')


