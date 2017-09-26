from collections import defaultdict

DIFFICULTY = 1 << 245
COINBASE_CONSTANT = "__COINBASE__"
COINBASE_AMT = 10.0

def tx_input(tx_out_hash, tx_index, tx_out_index):
    return (tx_out_hash, tx_index, tx_out_index)

def tx_output(out_addr, amt):
    return (out_addr, amt)

class Tx:
    def __init__(self, from_addr, inputs, outputs):
        self.from_addr = from_addr
        self.inputs = inputs
        self.outputs = outputs

    @classmethod
    def coinbase(cls, out_addr):
        return cls(COINBASE_CONSTANT, [], [tx_output(out_addr, COINBASE_AMT)])
    
    def amt_out(self):
        return sum(x[1] for x in self.outputs)
    
    def as_json(self):
        return {"from": self.from_addr, "inputs": self.inputs, "outputs": self.outputs}
    
    def is_coinbase(self):
        return self.from_addr == COINBASE_CONSTANT
    
    def total_output(self):
        return sum(x[1] for x in self.outputs)
    
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
        return {"id": self.id, "txs": self.txs, "nonce": self.nonce, "last": self.last_hash}
    
    @classmethod
    def genesis(cls):
        return cls(1, None, [], None)
    
    def __repr__(self):
        return "Block<{}>[{}]".format(fmt_h(hash_(self)), self.txs)

class BlockChain:
    def __init__(self):
        self.init_blocks()
        self.valid_inputs = self.find_inputs()

    def init_blocks(self):
        gen = BlockStruct.genesis()
        self.current_hash = hash_(gen)
        self.blocks = {self.current_hash: gen}
    
    def block_iter(self):
        h = self.current_hash
        while h is not None:
            b = self.blocks[h]
            yield b
            h = b.last_hash
    
    def find_inputs(self):
        valid_inputs = defaultdict(list)
        inputs = set()
        for block in self.block_iter():
            block_hash = hash_(block)
            for tx_index, tx in enumerate(block.txs):
                # An output is a valid input unless it's been consumed by another transaction
                for output_index, (addr, amt) in enumerate(tx.outputs):
                    output_id = (block_hash, tx_index, output_index)
                    if (output_id) not in inputs:
                        valid_inputs[addr].append(output_id)
                for out_h, out_idx, out_out_idx in tx.inputs:
                    inputs.add((out_h, out_idx, out_out_idx))
        print(valid_inputs)
        return valid_inputs
    
    def output_size(self, block_hash, tx_index, output_index):
        return self.blocks[block_hash].txs[tx_index].outputs[output_index][1]
    
    def holdings(self):
        return {user: sum(self.output_size(*x) for x in self.valid_inputs[user]) for user in self.valid_inputs}
            
                
    def last_block(self):
        return self.blocks[self.current_hash]
            
    def validate_block(self, block):
        # Doesn't handle missed blocks (yet)
        if block.last_hash != hash_(self.last_block()):
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
        if not all(inp in self.valid_inputs[tx.from_addr] for inp in tx.inputs):
            raise InvalidTransactionException("Transaction includes invalid/double-spend inputs".format(tx))
        if sum(self.output_size(*i) for i in tx.inputs) < tx.total_output():
            raise InvalidTransactionException("Transaction outputs are more than inputs")
            
    def __repr__(self):
        s = "Chain:\n" + "\n".join("\t{}: {}".format(str(hash_(blk))[:8], str(blk)) for blk in self.block_iter())
        s += "\n"
        return s
