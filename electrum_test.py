#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import sys
import os

local_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, local_path)

import nfc_terminal.blockchain as electrum_adapter

# for address in ["14PztPGEj4NErunhQYvWehBGRLq9shxu2P",
#                 "19yqsWTV5LidMGw5JCXqMxQzTnrg2EKiJy",
#                 "16HDgJ4xxBTH4VNtEWywnkc5hVbpQwmmmX",
#                 "1NfqHQVdaBHbYxmusjnRmxRA9yrGYMsB3H",
#                 "18oEwAiBYNwMddrY8xNz1ew3kBRMX7byc4",
#                 "12NCUyS2KyHtgFBsAEQTFL5mY3W4CchFF3",
#                 "1NGyHmWRpZs8gKidJmbrP2TpgsokRM3Ewh",
#                 "14GXCfUfyY5gGogXYzzpaocgJQvrVdYPxa",
#                 "1LwxPETXsCAReUStDpXUjnCHEy9YkRqKo9"
#                 ]:
#     balance = electrum_adapter.getAddressBalance(address)
#     print address + ' - ' + str(balance)

# data = electrum_adapter.getAddressBalance('1NfqHQVdaBHbYxmusjnRmxRA9yrGYMsB3H')
# data = electrum_adapter.getFreshAddress()
data = electrum_adapter.sendTransaction([('1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz', Decimal('3.9E-7')),
                                         ('1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz', Decimal('0.00007735'))],
                                        from_addr='17qJqwGw3BtoG2twm7W2PNsRHojPv98ED8')
print data


# fiat to pay: 0.01000000
# instantfiat: 0E-8
# merchant: 0.00007706
# fee: 0.00010039
# total: 0.00017745
#
# local address: 1NfqHQVdaBHbYxmusjnRmxRA9yrGYMsB3H
# instantfiat address: None
# merchant address: 1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz
# fee address: 1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz


# tx.sign(), keypairs: {'029496243f77bd1007b2e263f790e0f9fd5f4e1011fdfdd0e953c704d79986c7e0': 'L5biR9j4FbQ8BxT93HqxU6hn3CisyT8e68BvF7j7TN3PqzE4uhPo', '027c66f258a28aa82af8ae25d38e42a1cf05fb1611e2a29d827641b1f17110bb6e': 'L3MeTAvAnHdpqLzXFG4cQXoK5v2zP4SXwACUPaxFuPfAtVWYDghD'}
# adding signature for 027c66f258a28aa82af8ae25d38e42a1cf05fb1611e2a29d827641b1f17110bb6e
# adding signature for 029496243f77bd1007b2e263f790e0f9fd5f4e1011fdfdd0e953c704d79986c7e0
# False error: {u'message': u'TX rejected', u'code': -22}
# False
