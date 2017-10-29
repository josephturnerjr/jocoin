from .signature import is_valid_signature
from .hashing import hash_
from .serialization import fmt_h
from .util import ValueComparable

COINBASE_CONSTANT = ("__COINBASE__", 0)
COINBASE_AMT = 10.0

class TxOutput(ValueComparable):
    def __init__(self, out_addr, amount):
        self.out_addr = out_addr
        self.amount = amount

    def as_json(self):
        return self.__dict__

    @classmethod
    def from_json(cls, data):
        data["out_addr"] = tuple(data["out_addr"])
        return cls(**data)

    def __repr__(self):
        return "TxOutput<{}>".format(str(self.as_json()))

class TxInput(ValueComparable):
    def __init__(self, block_hash, tx_index, tx_out_index):
        self.block_hash = block_hash
        self.tx_index = tx_index
        self.tx_out_index = tx_out_index

    def as_json(self):
        return {
            "block_hash": self.block_hash,
            "tx_index": self.tx_index,
            "tx_out_index": self.tx_out_index
        }

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def __repr__(self):
        return "TxInput<{}>".format(str(self.as_json()))


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
    def coinbase(cls, out_addr):
        return cls(COINBASE_CONSTANT, None, [], [TxOutput(out_addr, COINBASE_AMT)])
    
    def amt_out(self):
        return sum(x.amount for x in self.outputs)
    
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
        data["inputs"] = [TxInput.from_json(i) for i in data["inputs"]]
        data["outputs"] = [TxOutput.from_json(o) for o in data["outputs"]]
        return cls(**data)
    
    def is_coinbase(self):
        return self.from_addr == COINBASE_CONSTANT
    
    def validate(self):
        if not is_valid_signature((self.inputs, self.outputs), self.signature, self.from_addr):
            raise InvalidTransactionException("Invalid signature")
    
    def __repr__(self):
        return "Tx<{}>[{} {} {}]".format(fmt_h(hash_(self)), self.from_addr, self.inputs, self.outputs)

class InvalidTransactionException(Exception):
    pass
