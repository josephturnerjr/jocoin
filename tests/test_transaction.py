import unittest

from jocoin.tx import Tx, TxInput, TxOutput, InvalidTransactionException
import jocoin.crypto as jc
import jocoin.signature as signature

class TestTx(unittest.TestCase):
    def setUp(self):
        keys = jc.gen_keys(256)
        self.pubkey = keys["pubkey"]
        self.privkey = keys["privkey"]
        self.inputs = [TxInput(1, 0, 0)]
        self.outputs = [TxOutput("YOU", 5.0), TxOutput("ME", 5.0)]

    def test_valid_signature(self):
        sig = signature.create_signature((self.inputs, self.outputs), self.privkey)
        valid = Tx(self.pubkey, sig, self.inputs, self.outputs)
        valid.validate()

    def test_invalid_signature(self):
        valid = Tx(self.pubkey, 30498230948, self.inputs, self.outputs)
        with self.assertRaises(InvalidTransactionException):
            valid.validate()

