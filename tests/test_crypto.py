import unittest
from mock import patch

import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


from xbterminal.helpers import crypto


class CryptoTestCase(unittest.TestCase):

    @patch('xbterminal.helpers.crypto.save_secret_key')
    def test_generate_keypair(self, save_key_mock):
        secret_key_pem, public_key_pem = crypto.generate_keypair()
        self.assertTrue(isinstance(secret_key_pem, str))
        self.assertTrue(isinstance(public_key_pem, str))

    @patch('xbterminal.helpers.crypto.read_secret_key')
    def test_signing(self, read_key_mock):
        secret_key_pem, public_key_pem = crypto.generate_keypair()
        read_key_mock.return_value = secret_key_pem

        message = str({
            'device': '1A2B4C',
            'amount': 10.0,
            'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
        })
        signature = crypto.create_signature(message)

        # Verify
        public_key = serialization.load_pem_public_key(
            public_key_pem, backend=default_backend())
        verifier = public_key.verifier(
            base64.b64decode(signature),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        verifier.update(message)
        result = verifier.verify()
        self.assertIsNone(result)
