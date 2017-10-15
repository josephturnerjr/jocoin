from collections import defaultdict
from .signature import create_signature, is_valid_signature
from .hashing import hash_
from .serialization import fmt_h

DIFFICULTY = 1 << 245
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

class InvalidBlockException(Exception):
    pass

class InvalidTransactionException(Exception):
    pass

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
    
    def __repr__(self):
        return "Block<{}>[{}]".format(fmt_h(hash_(self)), self.txs)

    def __eq__(self, other):
        return self.last_hash == other.last_hash and self.txs == other.txs and self.nonce == other.nonce


class BlockChain:
    def __init__(self, current_hash, blocks):
        ordered = list(self.block_iter_(current_hash, blocks))
        ordered.reverse()
        gen = BlockStruct.genesis()
        gen_hash = hash_(gen)
        if gen_hash in blocks and blocks[gen_hash] == gen:
            self.current_hash = gen_hash
            self.blocks = {gen_hash: gen}
            for block in ordered[1:]:
                self.add_block(block)
        else:
            print(gen_hash in blocks, blocks[gen_hash], gen)
            raise ValueError("Seed blocks do not contain the Genesis block")
        self.valid_inputs = self.find_inputs()

    @classmethod
    def empty(cls):
        gen = BlockStruct.genesis()
        current_hash = hash_(gen)
        blocks = {current_hash: gen}
        return cls(current_hash, blocks)

    def length(self):
        return len(list(self.block_iter()))

    def as_json(self):
        return {
            "blocks": {b: self.blocks[b].as_json() for b in self.blocks},
            "current_hash": self.current_hash
        }

    @classmethod
    def from_json(cls, data):
        data["blocks"] = {int(b): BlockStruct.from_json(data["blocks"][b]) for b in data["blocks"]}
        print(data)
        return cls(**data)
    
    def block_iter(self):
        return self.block_iter_(self.current_hash, self.blocks)

    @staticmethod
    def block_iter_(last_hash, blocks):
        h = last_hash
        while h is not None:
            b = blocks[h]
            yield b
            h = b.last_hash
        
    def find_inputs(self):
        valid_inputs = defaultdict(list)
        inputs = set()
        for block in self.block_iter():
            block_hash = hash_(block)
            for tx_index, tx in enumerate(block.txs):
                print(tx)
                # An output is a valid input unless it's been consumed by another transaction
                for output_index, (addr, amt) in enumerate(tx.outputs):
                    output_id = (block_hash, tx_index, output_index)
                    if output_id not in inputs:
                        valid_inputs[addr].append(output_id)
                for out_h, out_idx, out_out_idx in tx.inputs:
                    inputs.add((out_h, out_idx, out_out_idx))
        return valid_inputs
    
    def output_size(self, block_hash, tx_index, output_index):
        return self.blocks[block_hash].txs[tx_index].outputs[output_index][1]
    
    def holdings(self):
        return {user: sum(self.output_size(*x) for x in self.valid_inputs[user]) for user in self.valid_inputs}

    def valid_inputs_for(self, pubkey):
        return [(i, self.output_size(*i)) for i in self.valid_inputs[pubkey]]
                
    def last_block(self):
        return self.blocks[self.current_hash]
            
    def validate_block(self, block):
        # Doesn't handle missed blocks (yet)
        if block.last_hash != self.current_hash:
            raise InvalidBlockException("Last hash does not match last block in chain")
        # Validate nonce
        if not hash_(block) < DIFFICULTY:
            raise InvalidBlockException("Invalid nonce: {} is not less than {}".format(hash_(block), DIFFICULTY))
        # Validate transactions
        for tx in block.txs:
            try:
                self.validate_tx(tx)
            except InvalidTransactionException as e:
                raise InvalidBlockException("Invalid transaction in block {}: {}".format(tx, e))
    
    def add_block(self, blk):
        try:
            self.validate_block(blk)
            h = hash_(blk)
            self.blocks[h] = blk
            self.current_hash = h
            self.valid_inputs = self.find_inputs()
            return True
        except InvalidBlockException as e:
            print("Invalid block: {} {}".format(blk, e))
            return False
        
    def validate_coinbase(self, tx):
        if tx.amt_out() != COINBASE_AMT:
            raise InvalidTransactionException("Coinbase includes incorrect payout")
    
    def validate_tx(self, tx):
        if tx.is_coinbase():
            self.validate_coinbase(tx)
        else:
            self.validate_transaction(tx)
    
    def validate_transaction(self, tx):
        tx.validate()
        if not all(inp in self.valid_inputs[tx.from_addr] for inp in tx.inputs):
            raise InvalidTransactionException("Transaction includes invalid/double-spend inputs".format(tx))
        if sum(self.output_size(*i) for i in tx.inputs) < tx.total_output():
            raise InvalidTransactionException("Transaction outputs are more than inputs")
            
    def __repr__(self):
        s = "Chain:\n" + "\n".join("\t{}: {}".format(str(hash_(blk))[:8], str(blk)) for blk in self.block_iter())
        s += "\n"
        return s
