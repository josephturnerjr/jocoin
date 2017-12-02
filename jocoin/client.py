import random
from threading import Thread
from .chain import DIFFICULTY, BlockChain, BlockStruct, InvalidTransactionException
from .tx import Tx, TxOutput
from .serialization import serialize
from .hashing import hash_
from .signature import create_signature
from .jocoinlistener import JoCoinListener


class Client:
    def __init__(self, pubkey, privkey, network, peers):
        self.address = network.register(self)
        self.pubkey = pubkey
        self.privkey = privkey
        self.network = network
        self.current_txs = []
        self.chain = None
        if peers:
            self.peers = peers
        else:
            self.peers = []

    def start(self):
        # Initialize state
        if self.peers:
            self.get_initial_state()
        else:
            self.chain = BlockChain.empty()
        # Start listening thread
        listener = JoCoinListener(self)
        self.listen_process = Thread(target=listener.start)
        self.listen_process.start()
        # Start mining
        while True:
            block = self.mine()
            print("New block: {}".format(block))
            self.add_block(block)
            print("Chain length: {}".format(self.chain.length()))
        
        
    def random_peer(self):
        if self.peers:
            return random.choice(self.peers)

    def get_initial_state(self):
        while True:
            try:
                peer = self.random_peer()
                other = self.network.swap_history(peer, None)
                if other:
                    self.merge_history(other)
                    break
                else:
                    continue
            except ConnectionError as e:
                print("Error connecting to peer {}: {}").format(peer, e)
            except Exception as e:
                print("Error merging peer history for peer {}: {}").format(peer, e)
            time.sleep(1)

    def broadcast(self):
        # For newly-found blocks, blast to all known peers
        for peer in self.peers:
            self.gossip_with_peer(peer, self.get_all_state())

    def gossip(self):
        peer = self.random_peer()
        if peer is not None:
            #print("Sending {} my state: {}".format(peer, self.get_all_state()))
            return self.gossip_with_peer(peer, self.get_all_state())

    def gossip_with_peer(self, peer, history):
        other = self.network.swap_history(peer, history)
        self.handle_peer_data(other)

    def handle_peer_data(self, data):
        #print("Received this data during gossip: {}".format(data))
        if data:
            self.merge_history(data)

    def merge_history(self, other):
        self.merge_peers(other["peers"])
        self.merge_chain(BlockChain.from_json(other["chain"]))
        # Tx merge must happen after blockchain merge so that txs can be pruned
        self.merge_txs([Tx.from_json(tx) for tx in other["txs"]])

    def merge_peers(self, other_peers):
        self.peers = list(set().union(self.peers, other_peers) - set([self.address]))

    def merge_txs(self, other_txs):
        # Merge transaction lists
        current_txs = list(set().union(self.current_txs, other_txs))
        # Prune spent and invalid transactions
        self.current_txs = []
        for tx in current_txs:
            self.add_tx(tx)

    def merge_chain(self, other_chain):
        if self.chain is None:
            self.chain = other_chain
        else:
            # Lots of ways to optimize this
            # Basically here we're just taking the longest of the two (valid) chains
            if other_chain.length() > self.chain.length():
                self.chain = other_chain

    def get_all_state(self):
        return {
            "peers": [self.address] + self.peers,
            "txs": [tx.as_json() for tx in self.current_txs],
            "chain": self.chain.as_json()
        }

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
        return self.current_txs[:] + [Tx.coinbase(self.pubkey)]
        
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

    def get_inputs_for(self, pubkey):
        return self.chain.valid_inputs_for(pubkey)
