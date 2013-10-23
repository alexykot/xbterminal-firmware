#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

local_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, local_path)

import nfc_terminal.blockchain as electrum_adapter

# data = electrum_adapter.getAddressBalance('1vBnjSt5MZTQa6CCjZfRatgNX2hcBVJKW')
data = electrum_adapter.getFreshAddress()
# data = electrum_adapter.sendTransaction([('1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz', 0.0010)])
print data
