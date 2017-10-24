from .serialization import serialize, deserialize


class Connection:
    def __init__(self, state):
        self.state = state

    def send(self, msg, data):
        if msg == Network.SWAP:
            self.status = Network.SWAP
            self.state.handle_peer_data(data)
        else:
            raise ConnectionError("Unknown message type: {}").format(msg)

    def read(self):
        if self.status == Network.SWAP:
            state = self.state.get_all_state()
            return deserialize(serialize(state))
    

class Network:
    SWAP = "YO!"

    def __init__(self):
        self.index = 0
        self.peer_list = []

    def connect(self, peer_id):
        return Connection(self.peer_list[peer_id])

    def swap_history(self, peer_id, history):
        connection = self.connect(peer_id)
        connection.send(self.SWAP, deserialize(serialize(history)))
        return connection.read()

    def register(self, client):
        self.peer_list.append(client)
        client_index = self.index
        self.index += 1
        return client_index
