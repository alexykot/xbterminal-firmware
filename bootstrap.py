#!/usr/bin/python2.7
import sys
import os

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import nfc_terminal

nfc_terminal.main.main()