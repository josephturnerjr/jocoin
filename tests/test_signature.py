import unittest
from jocoin.signature import create_signature, is_valid_signature
from jocoin.crypto import gen_keys
import random
import string

def random_string(length):
    return "".join(random.choice(string.printable) for i in range(length))

class TestSignature(unittest.TestCase):
        
    def test_signature(self):
        keys = gen_keys(256)
        for i in range(100):
            l = random.getrandbits(10)
            m = random_string(l)
            s = create_signature(m, keys["privkey"])
            self.assertTrue(is_valid_signature(m, s, keys["pubkey"]))

