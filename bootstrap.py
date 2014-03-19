#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import subprocess
import time
import sys
import os
import logging

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

XBTERMINAL_MAIN_PATH = os.path.join(include_path, 'xbterminal', 'main.py')

main_proc_pid = None
while True:
    try:
        os.kill(main_proc_pid, 0)
    except (TypeError, OSError):
        main_proc_pid = None

    if main_proc_pid is None:
        try:
            main_proc = subprocess.call([XBTERMINAL_MAIN_PATH, ])
            main_proc_pid = main_proc.pid
        except Exception, error:
            logging.exception(error)

    time.sleep(1)