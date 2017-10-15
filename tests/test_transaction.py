import unittest

from jocoin.tx import Tx, tx_input, tx_output, InvalidTransactionException
import jocoin.crypto as jc

class TestTx(unittest.TestCase):
    def setUp(self):
        keys = jc.gen_keys(256)
        self.pubkey = keys["pubkey"]
        self.privkey = keys["privkey"]
        self.inputs = [tx_input(1, 0, 0)]
        self.outputs = [tx_output("YOU", 5.0), tx_output("ME", 5.0)]

    def test_valid_signature(self):
        valid = Tx.build_with_signature(self.pubkey, self.privkey, self.inputs, self.outputs)
        valid.validate()

    def test_invalid_signature(self):
        valid = Tx(self.pubkey, 30498230948, self.inputs, self.outputs)
        with self.assertRaises(InvalidTransactionException):
            valid.validate()

