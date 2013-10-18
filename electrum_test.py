#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

local_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, local_path)

import nfc_terminal.blockchain as electrum_adapter


data = electrum_adapter.getAddressBalance('1NHbJbCt69BmM4kXBq6DJ9JB9MZh2xhh3E')
# data = electrum_adapter.getFreshAddress()
# data = electrum_adapter.sendTransaction([('1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz', 0.0001), ("1EG9WVHe2LSBEQUkxWL4aJDnVtpoULwfSb", 0.0001)],
#                                         from_addr='1NHbJbCt69BmM4kXBq6DJ9JB9MZh2xhh3E')

print ''
print '<<<'
print data
print '>>>'
print ''





