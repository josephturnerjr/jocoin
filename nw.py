from jocoin.network import Network
from jocoin.client import Client
from jocoin.tx import TxOutput
import pprint
import jocoin.crypto as jc


def create_client(network, peers):
    keys = jc.gen_keys()
    return Client(keys["pubkey"], keys["privkey"], network, peers)


if __name__ == "__main__":
    n = Network()
    c0 = create_client(n, [])
    c1 = create_client(n, [0])
    b = c1.mine()
    c1.add_block(b)
    c2 = create_client(n, [0, 1])

    for x in range(1):
        for c in n.peer_list:
            c.gossip()

    #for i, c in enumerate(n.peer_list):
    #    print(i, pprint.pformat(c.get_all_state()))

    tx = c0.make_tx_for(c1.privkey, c1.pubkey, [TxOutput(c0.pubkey, 1.0)])
    print("c0", pprint.pformat(c0.chain.holdings()))
    print("c1", pprint.pformat(c1.chain.holdings()))
    print("c2", pprint.pformat(c2.chain.holdings()))
    c0.add_tx(tx)

    #print("After tx, but before gossip")
    #for i, c in enumerate(n.peer_list):
    #    print(i, pprint.pformat(c.get_all_state()))
    #print("c0", pprint.pformat(c0.chain.holdings()))
    #print("c1", pprint.pformat(c1.chain.holdings()))
    #b = c0.mine()
    #c0.add_block(b)
    print("After adding new tx")
    #for i, c in enumerate(n.peer_list):
    #    print(i, pprint.pformat(c.get_all_state()))

    print("c0", pprint.pformat(c0.chain.holdings()))
    print("c1", pprint.pformat(c1.chain.holdings()))
    print("c2", pprint.pformat(c2.chain.holdings()))
    
    c1.gossip()

    print("After gossip")
    #for i, c in enumerate(n.peer_list):
    #    print(i, pprint.pformat(c.get_all_state()))

    b = c1.mine()
    c1.add_block(b)
    c1.broadcast()

    print("After mining")
    print("c0", pprint.pformat(c0.chain.holdings()))
    print("c0", pprint.pformat(c0.chain.find_inputs()))
    print("c1", pprint.pformat(c1.chain.holdings()))
    print("c0", pprint.pformat(c1.chain.find_inputs()))
    print("c2", pprint.pformat(c2.chain.holdings()))
    print("c0", pprint.pformat(c2.chain.find_inputs()))
    for i, c in enumerate(n.peer_list):
        print(i, pprint.pformat(c.get_all_state()))
