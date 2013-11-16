#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults
import xbterminal.instantfiat
import xbterminal.instantfiat.bitpay

xbterminal.defaults.PROJECT_ABS_PATH = include_path

xbterminal.instantfiat.bitpay.isInvoicePaid('SRaGrckR9gkbLkC1rc7L6y')