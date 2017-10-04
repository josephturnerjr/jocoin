from jocoin import network
from jocoin import client

if __name__ == "__main__":
    clients = []
    n = network.Network(clients)
    c0 = client.Client(n, [])
    clients.append(c0)
    c1 = client.Client(n, [0])
    clients.append(c1)
    b = c1.mine()
    c1.add_block(b)
    c2 = client.Client(n, [1])
