import unittest

from xbterminal.gui.utils.addresses import is_valid_address


class IsValidAddressTestCase(unittest.TestCase):

    def test_btc(self):
        address_1 = '14Bg5acQDJgKsWrAKUyQNtD44Y2yQgz5KS'
        self.assertIs(is_valid_address(address_1, 'BTC'), True)
        address_2 = '3ELAsRvCtSNYC2CuEFZGCBhWxtDf3hxc9c'
        self.assertIs(is_valid_address(address_2, 'BTC'), True)
        address_3 = 'mmoCp8HdjvJjVHFi9hhGg9eVRAUW9AGHch'
        self.assertIs(is_valid_address(address_3, 'BTC'), False)

    def test_tbtc(self):
        address_1 = 'mmoCp8HdjvJjVHFi9hhGg9eVRAUW9AGHch'
        self.assertIs(is_valid_address(address_1, 'TBTC'), True)
        address_2 = 'n3hWQvZy6SNZq2LoFUskDmUpWXBvYZy4ug'
        self.assertIs(is_valid_address(address_2, 'TBTC'), True)
        address_3 = '2Mz9yDmGqPrVR8nCaFJcvNWM2eRtVsrmotz'
        self.assertIs(is_valid_address(address_3, 'TBTC'), True)
        address_4 = '3ELAsRvCtSNYC2CuEFZGCBhWxtDf3hxc9c'
        self.assertIs(is_valid_address(address_4, 'TBTC'), False)

    def test_dash(self):
        address_1 = 'Xv6J4DJtmLMbWEmUaqJEFhQXS2ToMJvDR7'
        self.assertIs(is_valid_address(address_1, 'DASH'), True)
        address_2 = '14Bg5acQDJgKsWrAKUyQNtD44Y2yQgz5KS'
        self.assertIs(is_valid_address(address_2, 'DASH'), False)

    def test_tdash(self):
        address_1 = 'yfyzM58VsmjfbXtTzNrYH14TmJvY3Nn3Ms'
        self.assertIs(is_valid_address(address_1, 'TDASH'), True)
        address_2 = 'Xv6J4DJtmLMbWEmUaqJEFhQXS2ToMJvDR7'
        self.assertIs(is_valid_address(address_2, 'TDASH'), False)
