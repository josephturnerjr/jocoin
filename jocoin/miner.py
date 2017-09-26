from .chain import DIFFICULTY, BlockChain, InvalidTransactionException


class Miner:
    def __init__(self):
        self.current_txs = []
        self.chain = BlockChain()
        
    def add_tx(self, tx):
        # Add transaction to list of candidates
        try:
            self.chain.validate_tx(tx)
            self.current_txs.append(tx)
            return True
        except InvalidTransactionException as e:
            print("Invalid transaction {}: {}".format(tx, e))
            return False
    
    def emit_txs(self):
        # Export transaction candidates with coinbase for block mining
        self.add_tx(Tx.coinbase("ME"))
        txs = self.current_txs
        self.current_txs = []
        return txs
        
    def mine(self):
        # Find a valid block based on candidates
        hash_max = self.calculate_difficulty()
        nonce = 0x0
        txs = self.emit_txs()
        obj_s = serialize(txs)
        last = self.chain.last_block()
        bs = BlockStruct(last.id + 1, hash_(last), txs, nonce)
        while True:
            h = hash_(bs)        
            if h < hash_max:
                return bs
            bs.nonce += 1
            
    def calculate_difficulty(self):
        # TODO calculate difficulty
        return DIFFICULTY
    
    def add_block(self, blk):
        return self.chain.add_block(blk)
