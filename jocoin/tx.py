from .signature import create_signature, is_valid_signature
from .hashing import hash_
from .serialization import fmt_h

COINBASE_CONSTANT = ("__COINBASE__", 0)
COINBASE_AMT = 10.0

def tx_input(tx_out_hash, tx_index, tx_out_index):
    return (tx_out_hash, tx_index, tx_out_index)

def tx_output(out_addr, amt):
    return (tuple(out_addr), amt)

class Tx:
    def __init__(self, from_addr, signature, inputs, outputs):
        self.from_addr = from_addr
        self.signature = signature
        self.inputs = inputs
        self.outputs = outputs

    def __hash__(self):
        return self.signature

    def __eq__(self, other):
        return self.from_addr == other.from_addr and self.signature == other.signature and self.inputs == other.inputs and self.outputs == other.outputs

    @classmethod
    def build_with_signature(cls, pubkey, privkey, inputs, outputs):
        sig = create_signature((inputs, outputs), privkey)
        return Tx(pubkey, sig, inputs, outputs)

    @classmethod
    def coinbase(cls, out_addr):
        return cls(COINBASE_CONSTANT, None, [], [tx_output(out_addr, COINBASE_AMT)])
    
    def amt_out(self):
        return sum(x[1] for x in self.outputs)
    
    def as_json(self):
        return {
            "from_addr": self.from_addr,
            "signature": self.signature,
            "inputs": self.inputs,
            "outputs": self.outputs
        }

    @classmethod
    def from_json(cls, data):
        data["from_addr"] = tuple(data["from_addr"])
        data["inputs"] = [tx_input(*i) for i in data["inputs"]]
        data["outputs"] = [tx_output(*o) for o in data["outputs"]]
        return cls(**data)
    
    def is_coinbase(self):
        return self.from_addr == COINBASE_CONSTANT
    
    def total_output(self):
        return sum(x[1] for x in self.outputs)

    def validate(self):
        if not is_valid_signature((self.inputs, self.outputs), self.signature, self.from_addr):
            raise InvalidTransactionException("Invalid signature")
    
    def __repr__(self):
        return "Tx<{}>[{} {} {}]".format(fmt_h(hash_(self)), self.from_addr, self.inputs, self.outputs)

class InvalidTransactionException(Exception):
    pass
