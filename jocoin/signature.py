from .hashing import hash_
from .crypto import encrypt, decrypt


def create_signature(m, privkey):
    h = hash_(m)
    return encrypt(h, privkey)

def is_valid_signature(m, signature, pubkey):
    h = hash_(m)
    return decrypt(signature, pubkey) == h

