from .hashing import hash_
from .serialization import fmt_h
from .tx import Tx


class BlockStruct:
    def __init__(self, id, last_hash, txs, nonce):
        self.id = id
        self.last_hash = last_hash
        self.txs = txs
        self.nonce = nonce
    
    def as_json(self):
        return {
            "id": self.id,
            "txs": self.txs,
            "nonce": self.nonce,
            "last_hash": self.last_hash
        }

    @classmethod
    def from_json(cls, data):
        data["txs"] = [Tx.from_json(tx) for tx in data["txs"]]
        return cls(**data)
    
    @classmethod
    def genesis(cls):
        return cls(1, None, [], None)

    def coinbase(self):
        return [tx for tx in self.txs if tx.is_coinbase()][0]

    def miner(self):
        return self.coinbase().outputs[0].out_addr
    
    def __repr__(self):
        return "Block<{}>[{}]".format(fmt_h(hash_(self)), self.txs)

    def __eq__(self, other):
        return self.last_hash == other.last_hash and self.txs == other.txs and self.nonce == other.nonce
