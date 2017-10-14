from jocoin.network import Network
from jocoin.client import Client

if __name__ == "__main__":
    clients = []
    n = Network(clients)
    c0 = Client(n, [])
    clients.append(c0)
    c1 = Client(n, [0])
    clients.append(c1)
    b = c1.mine()
    c1.add_block(b)
    c2 = Client(n, [1])
    clients.append(c2)

    for i, c in enumerate(clients):
        print(i, c.get_all_state())

    for x in range(10):
        for c in clients:
            c.gossip()

    for i, c in enumerate(clients):
        print(i, c.get_all_state())
