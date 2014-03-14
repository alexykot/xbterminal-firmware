#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import logging
from pbkdf2 import PBKDF2

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults
import xbterminal.stages
import xbterminal.main

xbterminal.defaults.PROJECT_ABS_PATH = include_path

logging.basicConfig(level=logging.DEBUG)

try:
    xbterminal.main.main()
except Exception, error:
    logging.exception(error)
    xbterminal.stages.gracefullExit()