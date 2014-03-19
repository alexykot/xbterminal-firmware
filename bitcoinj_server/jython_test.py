#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import time

print 'spawned!'

with open('/root/XBTerminal/bitcoinj_server/runtime/debug.log', 'a+') as test_file:
    test_file.write("test \n")

time.sleep(1)
print 'spawn dies'



#!/opt/jython/jython -Dorg.slf4j.simpleLogger.defaultLogLevel=error -v
