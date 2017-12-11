import random
import time
import traceback
from threading import Thread, RLock
from .chain import DIFFICULTY, BlockChain, BlockStruct, InvalidTransactionException
from .tx import Tx, TxOutput
from .serialization import serialize
from .hashing import hash_
from .signature import create_signature
from . import network as nw


class Client:
    GOSSIP_INTERVAL = 10

    def __init__(self, pubkey, privkey, peers, listen_addr):
        self.address = listen_addr
        self.pubkey = pubkey
        self.privkey = privkey
        self.current_txs = []
        self.chain = None
        if peers:
            self.peers = peers
        else:
            self.peers = []
        self.keep_mining = True
        self.keep_gossiping = True

    def start(self):
        # Initialize state
        if self.peers:
            self.get_initial_state()
        else:
            self.chain = BlockChain.empty()
        # Create lock for the state
        self.chain_lock = RLock()
        # Start listening thread
        listener = nw.JoCoinListener(self, self.address)
        self.listener = Thread(target=listener.start)
        self.listener.start()
        # Start gossiping
        self.gossiper = Thread(target=self.gossip_thread)
        self.gossiper.start()
        # Start mining
        self.mining_thread()

    def mining_thread(self):
        while True:
            print("Entering mining loop:")
            self.print_current_state()
            self.keep_mining = True
            # The chain lock is acquired inside the following call in order
            # to generate the transactions, and released afterwards
            block = self.mine()
            if block:
                print("New block found! Broadcasting to peers.")
                self.add_block(block)
                self.broadcast()

    def gossip_thread(self):
        while self.keep_gossiping:
            with self.chain_lock:
                self.gossip()
            time.sleep(self.GOSSIP_INTERVAL)
        
    def dispatch_incoming_message(self, message, data):
        with self.chain_lock:
            # Incoming data is already deserialized, but may be in nonstandard formats
            # (e.g. keys deserialize to lists instead of tuples)
            if message == nw.GOSSIP:
                return self.handle_peer_data(data)
            elif message == nw.BALANCE:
                pubkey = tuple(data)
                return self.holdings_for(pubkey)
            elif message == nw.INPUTS:
                pubkey = tuple(data)
                return self.inputs_for(pubkey)
            elif message == nw.TRANSFER:
                tx = Tx.from_json(data)
                if self.add_tx(tx):
                    return "SUCCESS"
                else:
                    return "FAILURE"
            else:
                print("Unknown message type: {}".format(message))

    def print_current_state(self, prefix="\t"):
        print(prefix + "Chain length: {}".format(self.chain.length()))
        print(prefix + "Last hash: {}...".format(str(self.chain.current_hash)[:6]))
        holdings = self.chain.holdings()
        print(prefix + "Holdings:")
        for (pk, e) in holdings:
            print(prefix + "\t{}...: {}".format(str(pk)[:6], holdings[(pk, e)]))
        
    def get_initial_state(self):
        while True:
            try:
                peer = self.random_peer()
                other = nw.gossip_with(peer, None)
                if other:
                    self.merge_history(other)
                    break
                else:
                    continue
            except ConnectionError as e:
                print("Error connecting to peer {}: {}".format(peer, e))
                traceback.print_exc()
            except Exception as e:
                print("Error merging peer history for peer {}: {}".format(peer, e))
                traceback.print_exc()
            time.sleep(1)

    def broadcast(self):
        # For newly-found blocks, blast to all known peers
        for peer in self.peers:
            self.gossip_with_peer(peer, self.get_all_state())

    def random_peer(self):
        if self.peers:
            return random.choice(self.peers)

    def gossip(self):
        peer = self.random_peer()
        if peer is not None:
            print("Gossiping with {}".format(peer))
            return self.gossip_with_peer(peer, self.get_all_state())

    def gossip_with_peer(self, peer, history):
        try:
            other = nw.gossip_with(peer, history)
            self.handle_peer_data(other)
        except Exception as e:
            print("Error gossiping with peer {}: {}".format(peer, e))

    def handle_peer_data(self, data):
        if data:
            self.merge_history(data)
        return self.get_all_state()

    def merge_history(self, other):
        self.merge_peers(other["peers"])
        self.merge_chain(BlockChain.from_json(other["chain"]))
        # Tx merge must happen after blockchain merge so that txs can be pruned
        self.merge_txs([Tx.from_json(tx) for tx in other["txs"]])

    def merge_peers(self, other_peers):
        self.peers = list(set().union(self.peers, map(tuple, other_peers)) - set([self.address]))

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
                self.keep_mining = False
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
        with self.chain_lock:
            txs = self.emit_txs()
            last = self.chain.last_block()
        bs = BlockStruct(last.id + 1, hash_(last), txs, nonce)
        while self.keep_mining:
            h = hash_(bs)        
            if h < hash_max:
                return bs
            bs.nonce += 1
            
    def calculate_difficulty(self):
        # TODO calculate difficulty
        return DIFFICULTY
    
    def add_block(self, blk):
        return self.chain.add_block(blk)

    def inputs_for(self, pubkey):
        return self.chain.valid_inputs_for(pubkey)

    def holdings_for(self, pubkey):
        return self.chain.holdings().get(pubkey, 0.0)

        
