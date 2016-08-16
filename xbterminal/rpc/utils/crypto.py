import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from xbterminal.rpc.settings import SECRET_KEY_FILE_PATH


def save_secret_key(pem):
    with open(SECRET_KEY_FILE_PATH, 'w') as key_file:
        key_file.write(pem)


def read_secret_key():
    with open(SECRET_KEY_FILE_PATH, 'r') as key_file:
        return key_file.read()


def generate_keypair():
    """
    Saves secret key to file and returns public key
    """
    secret_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())
    secret_pem = secret_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())

    public_key = secret_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return secret_pem, public_pem


def create_signature(message):
    secret_key = serialization.load_pem_private_key(
        read_secret_key(),
        password=None,
        backend=default_backend())
    signer = secret_key.signer(
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256())
    signer.update(message)
    signature = signer.finalize()
    return base64.b64encode(signature)


if __name__ == '__main__':
    secret_pem, public_pem = generate_keypair()
    save_secret_key(secret_pem)
    print(public_pem)
