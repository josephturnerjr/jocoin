from jocoin.network import Network
from jocoin.client import Client
import jocoin.crypto as jc


def create_client(network, peers):
    keys = jc.gen_keys()
    return Client(keys["pubkey"], keys["privkey"], network, peers)


if __name__ == "__main__":
    clients = []
    n = Network(clients)
    c0 = create_client(n, [])
    clients.append(c0)
    c1 = create_client(n, [0])
    clients.append(c1)
    b = c1.mine()
    c1.add_block(b)
    c2 = create_client(n, [1])
    clients.append(c2)

    for i, c in enumerate(clients):
        print(i, c.get_all_state())

    for x in range(10):
        for c in clients:
            c.gossip()

    for i, c in enumerate(clients):
        print(i, c.get_all_state())

    tx = c0.make_tx_for(c1.privkey, c1.pubkey, [(c2.pubkey, 1.0)])
    c0.add_tx(tx)

    for i, c in enumerate(clients):
        print(i, c.get_all_state())
    for x in range(10):
        for c in clients:
            c.gossip()

    for i, c in enumerate(clients):
        print(i, c.get_all_state())

    b = c2.mine()
    c2.add_block(b)
    c2.broadcast()

    for i, c in enumerate(clients):
        print(i, c.get_all_state())

