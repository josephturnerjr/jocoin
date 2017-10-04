import random


class Connection:
    def __init__(self, state):
        self.state = state

    def send(self, msg):
        if msg == Network.INITIATE:
            self.status = Network.INITIATE
        else:
            raise ConnectionError("Unknown message type: {}").format(msg)

    def read(self):
        if self.status == Network.INITIATE:
            return self.state.get_all_state()
    

class Network:
    INITIATE = "YO!"

    def __init__(self, peer_list):
        self.peer_list = peer_list

    def connect(self, peer_id):
        return Connection(self.peer_list[peer_id])

    def request_history(self, peer_id):
        connection = self.connect(peer_id)
        connection.send(self.INITIATE)
        return connection.read()
