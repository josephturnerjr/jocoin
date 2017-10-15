from collections import defaultdict
from .hashing import hash_
from .serialization import fmt_h
from .tx import Tx, InvalidTransactionException, COINBASE_AMT
from .blockstruct import BlockStruct

DIFFICULTY = 1 << 245

class InvalidBlockException(Exception):
    pass

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
