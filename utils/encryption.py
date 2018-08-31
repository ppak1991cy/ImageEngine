import rsa

from config import PRIVATEKEY_PATH


def load_priv_key(path):
    with open(path) as f:
        p = f.read()
        priv_key = rsa.PrivateKey.load_pkcs1(p)
    return priv_key


_privkey = load_priv_key(path=PRIVATEKEY_PATH)


def generate_sign(message):
    signn = rsa.sign(message, _privkey, 'SHA-1')
    return signn
