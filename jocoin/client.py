import random
from .chain import DIFFICULTY, BlockChain, BlockStruct, InvalidTransactionException, Tx
from .serialization import serialize
from .hashing import hash_


class Client:
    def __init__(self, network, peers):
        self.network = network
        if peers:
            self.peers = peers
            self.initiate_connection()
        else:
            self.peers = []
            self.current_txs = []
            self.chain = BlockChain.empty()
        
    def random_peer(self):
        if self.peers:
            return random.choice(self.peers)

    def initiate_connection(self):
        while True:
            try:
                peer = self.random_peer()
                other = self.network.request_history(peer)
                print("Initializing with ", other)
                self.peers = list(set().union(self.peers, other["peers"]))
                self.chain = BlockChain(**other["chain"])
                self.current_txs = other["txs"]
                break
            except ConnectionError as e:
                print("Error connecting to peer {}: {}").format(peer, e)
                time.sleep(1)

    def get_all_state(self):
        return {"peers": self.peers, "txs": self.current_txs, "chain": self.chain.serializable()}

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

    def make_tx_for(self, privkey, pubkey, outputs):
        all_inputs = self.chain.get_valid_inputs_for(pubkey)
        out_total = sum(x[1] for x in outputs)
        in_available = sum(x[1] for x in all_inputs)
        if out_total > in_available:
            raise InvalidTransactionException("Requested amount is larger than available funds")
        sum = 0.0
        inputs = []
        for i, amt in all_inputs:
            if sum < out_total:
                inputs.append(i)
                sum += amt
            else:
                break
        return Tx.build_with_signature(pubkey, privkey, inputs, outputs)
