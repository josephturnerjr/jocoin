import random
from .chain import DIFFICULTY, BlockChain, BlockStruct, InvalidTransactionException, Tx
from .serialization import serialize
from .hashing import hash_


class Client:
    def __init__(self, network, peers):
        self.network = network
        self.current_txs = []
        if peers:
            self.peers = peers
            self.chain = None
            self.get_initial_state()
        else:
            self.peers = []
            self.chain = BlockChain.empty()
        
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
            gossip_with_peer(peer)

    def gossip(self):
        peer = self.random_peer()
        if peer is not None:
            return self.gossip_with_peer(peer, self.get_all_state())

    def gossip_with_peer(self, peer, history):
        other = self.network.swap_history(peer, history)
        print("Gossiping with {} [{}] (sent {}, recieved {})".format(peer, self.peers, history, other))
        self.handle_peer_data(other)

    def handle_peer_data(self, data):
        if data:
            self.merge_history(data)

    def merge_history(self, other):
        self.merge_peers(other["peers"])
        self.merge_chain(BlockChain(**other["chain"]))
        # Tx merge must happen after blockchain merge so that txs can be pruned
        self.merge_txs(other["txs"])

    def merge_peers(self, other_peers):
        self.peers = list(set().union(self.peers, other_peers))

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
            "peers": self.peers,
            "txs": self.current_txs,
            "chain": self.chain.serializable()
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
