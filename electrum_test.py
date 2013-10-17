#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
from sys import stdout
import tempfile
import time

local_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, local_path)

import nfc_terminal
import nfc_terminal.blockchain
import nfc_terminal.blockchain.electrum as electrum_adapter


# print electrum_adapter.sendTransaction([("1LJkHHAzyohcfrVZ8f566k1yZeo5zuvuzx", 0.0001), ('1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz', 0.0003)],
#                                        source_address="1FFNPxzV4Pc1vx9AfQAba4kzJTy3g9aJX8")
print electrum_adapter.getAddressBalance("1FFNPxzV4Pc1vx9AfQAba4kzJTy3g9aJX8")


# ./electrum paytomany -v -f 0.0001 -s 1EG9WVHe2LSBEQUkxWL4aJDnVtpoULwfSb 183KCx8Tcc8faBf1Z1cug5bHWR9ZBkfgSm 0.0001 1HdrqJG7GJLdXsAeBo1KQQDsNi5PyBPAc6 0.0001 1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz 0.0001
# ./electrum paytomany -v -f 0.0001 -F 179Aw6Ej29vNSHi1zrsYzFHz49xUZnqXFT 183KCx8Tcc8faBf1Z1cug5bHWR9ZBkfgSm 0.0001 1HdrqJG7GJLdXsAeBo1KQQDsNi5PyBPAc6 0.0001

# ./electrum paytomany -v -f 0.0001 --wallet=/root/electrum/electrum.dat --fromaddr=183KCx8Tcc8faBf1Z1cug5bHWR9ZBkfgSm 179Aw6Ej29vNSHi1zrsYzFHz49xUZnqXFT 0.0002 1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz 0.0001
# ./electrum listaddresses -ab --wallet=/root/electrum/electrum.dat
# ./electrum --gui=stdio
# ./electrum payto -f 0.0001 --fromaddr=179Aw6Ej29vNSHi1zrsYzFHz49xUZnqXFT 1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz 0.0001
