import unittest
from jocoin.crypto import sieve, gen_keys, likely_prime, generate_prime, encrypt, decrypt
import random

def validate_prime(p):
    for i in range(2, int(p**(1/2)) + 2):
        if p % i == 0:
            print(p, i)
            return False
    return True

class TestCrypto(unittest.TestCase):
    BITLENGTH = 128
    
    def test_encryption_bounds(self):
        keys = gen_keys(self.BITLENGTH)
        priv = keys["privkey"]
        too_big = random.getrandbits(8 * self.BITLENGTH)
        with self.assertRaises(ValueError):
            encrypt(too_big, priv)
        too_small = -1
        with self.assertRaises(ValueError):
            encrypt(too_small, priv)
        # Valid ranges, should not raise
        encrypt(0, priv)
        encrypt(1, priv)
        for x in range(100):
            encrypt(random.randint(0, priv[0]), priv)

    def test_encryption_roundtrip(self):
        keys = gen_keys(self.BITLENGTH)
        priv = keys["privkey"]
        pub = keys["pubkey"]
        m = random.randint(0, priv[0])
        cypher = encrypt(m, priv)
        self.assertTrue(cypher != m)
        self.assertTrue(decrypt(cypher, pub) == m)
        

    def test_prime_generation(self):
        for i in range(1000):
            self.assertTrue(validate_prime(generate_prime(16)))

    def test_likely_prime(self):
        self.assertFalse(likely_prime(221))

    def test_sieve(self):
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        self.assertTrue(primes == sieve(100))
