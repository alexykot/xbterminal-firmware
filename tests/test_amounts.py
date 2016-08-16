# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
from mock import patch

from xbterminal.gui.utils import amounts


@patch.dict('xbterminal.gui.utils.amounts.state',
            remote_config={
                'language': {
                    'code': 'en',
                    'thousands_split': ',',
                    'fractional_split': '.',
                },
                'currency': {
                    'prefix': '$',
                },
            })
class AmountsUtilsTestCase(unittest.TestCase):

    def test_format_fiat_amount_pretty(self):
        amount = Decimal('3513.00')
        result = amounts.format_fiat_amount_pretty(amount)
        self.assertEqual(result, u'3,513.00')
        result = amounts.format_fiat_amount_pretty(amount, prefix=True)
        self.assertEqual(result, u'$3,513.00')

    def test_format_btc_amount_pretty(self):
        amount = Decimal('0.21231923')
        result = amounts.format_btc_amount_pretty(amount)
        self.assertIn(u'212.31<span style="font-size: small;">923</span>',
                      result)
        result = amounts.format_btc_amount_pretty(amount, frac2_size='12px')
        self.assertIn(u'212.31<span style="font-size: 12px;">923</span>',
                      result)
        result = amounts.format_btc_amount_pretty(amount, prefix=True)
        self.assertIn(u'm฿212.31<span style="font-size: small;">923</span>',
                      result)

    def test_format_exchange_rate_pretty(self):
        amount = Decimal('241.8')
        result = amounts.format_exchange_rate_pretty(amount)
        self.assertEqual(result, u'1 BTC = $241.80')
