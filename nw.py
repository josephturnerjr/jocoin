import sys
import json
from jocoin.client import Client
from jocoin.tx import TxOutput
from jocoin.user import make_tx_with_fee



def read_keyfile(fn):
    with open(fn) as f:
        return json.loads(f.read())


if __name__ == "__main__":
    keyfile, listen_addr, listen_port = sys.argv[1:4]
    listen_addr = (listen_addr, int(listen_port))
    if len(sys.argv) >= 5:
        peer_addr, peer_port = sys.argv[4:6]
        peers = [(peer_addr, int(peer_port))]
    else:
        peers = []
    keys = read_keyfile(keyfile)
    c = Client(tuple(keys["pubkey"]), tuple(keys["privkey"]), peers, listen_addr)
    c.start()
#    c1 = create_client(n, [0])
#
#    b = c1.mine()
#    c1.add_block(b)
#    c2 = create_client(n, [0, 1])
#
#    for x in range(1):
#        for c in n.peer_list:
#            c.gossip()
#
#    #for i, c in enumerate(n.peer_list):
#    #    print(i, pprint.pformat(c.get_all_state()))
#
#    tx = make_tx_with_fee(c0.get_inputs_for(c1.pubkey), c1.privkey, c1.pubkey, [TxOutput(c0.pubkey, 1.0)], 0.1)
#    print("c0", pprint.pformat(c0.chain.holdings()))
#    print("c1", pprint.pformat(c1.chain.holdings()))
#    print("c2", pprint.pformat(c2.chain.holdings()))
#    c0.add_tx(tx)
#
#    #print("After tx, but before gossip")
#    #for i, c in enumerate(n.peer_list):
#    #    print(i, pprint.pformat(c.get_all_state()))
#    #print("c0", pprint.pformat(c0.chain.holdings()))
#    #print("c1", pprint.pformat(c1.chain.holdings()))
#    #b = c0.mine()
#    #c0.add_block(b)
#    print("After adding new tx")
#    #for i, c in enumerate(n.peer_list):
#    #    print(i, pprint.pformat(c.get_all_state()))
#
#    print("c0", pprint.pformat(c0.chain.holdings()))
#    print("c1", pprint.pformat(c1.chain.holdings()))
#    print("c2", pprint.pformat(c2.chain.holdings()))
#    
#    c1.gossip()
#
#    print("After gossip")
#    #for i, c in enumerate(n.peer_list):
#    #    print(i, pprint.pformat(c.get_all_state()))
#
#    b = c1.mine()
#    c1.add_block(b)
#    c1.broadcast()
#
#    print("After mining")
#    print("c0", pprint.pformat(c0.chain.holdings()))
#    print("c0", pprint.pformat(c0.chain.find_inputs()))
#    print("c1", pprint.pformat(c1.chain.holdings()))
#    print("c0", pprint.pformat(c1.chain.find_inputs()))
#    print("c2", pprint.pformat(c2.chain.holdings()))
#    print("c0", pprint.pformat(c2.chain.find_inputs()))
#    for i, c in enumerate(n.peer_list):
#        print(i, pprint.pformat(c.get_all_state()))
