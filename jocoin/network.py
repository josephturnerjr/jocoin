import socket
import socketserver
import enum
from .serialization import serialize, deserialize
from .tx import Tx


GOSSIP = "GOSSIP"
BALANCE = "BALANCE"
INPUTS = "INPUTS"
TRANSFER = "TRANSFER"

def format_object_for_transmission(o):
    return format_string_for_transmission(serialize(o))

def format_string_for_transmission(s):
    return bytes(s + "\n", "utf-8")

class RAIISocket:
    def __init__(self, peer):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer = peer

    def __enter__(self):
        self.sock.connect(self.peer)
        return self.sock

    def __exit__(self, type, value, traceback):
        self.sock.close()

def send_message(peer, message_type, raw_data):
    msg_line = format_string_for_transmission(message_type)
    data_line = format_object_for_transmission(raw_data)
    with RAIISocket(peer) as sock:
        sock.sendall(msg_line + data_line)
        serialized_received = readline(sock)
    received = deserialize(serialized_received)
    return received
    
def request_transfer(peer, tx):
    return send_message(peer, TRANSFER, tx)

def request_balance(peer, public_key):
    return send_message(peer, BALANCE, public_key)

def request_inputs(peer, public_key):
    return send_message(peer, INPUTS, public_key)

def gossip_with(peer, client_state):
    return send_message(peer, GOSSIP, client_state)

def readline(sock, bufsize=4096):
    buf = ''
    data = True
    while data:
        data = str(sock.recv(bufsize), "utf-8")
        buf += data
        if '\n' in buf:
            return buf.splitlines()[0]

def data_from_request(req_line):
    return deserialize(req_line.strip())

class JoCoinServer(socketserver.StreamRequestHandler):
    def handle(self):
        message = self.get_message()
        if message == GOSSIP:
            peer_data = self.get_message_data()
            self.wfile.write(format_object_for_transmission(self.server.client.get_all_state()))
            self.server.client.handle_peer_data(peer_data)
        elif message == BALANCE:
            pubkey = tuple(self.get_message_data())
            self.wfile.write(format_object_for_transmission(self.server.client.holdings_for(pubkey)))
        elif message == INPUTS:
            pubkey = tuple(self.get_message_data())
            self.wfile.write(format_object_for_transmission(self.server.client.inputs_for(pubkey)))
        elif message == TRANSFER:
            tx = Tx.from_json(data_from_request(self.rfile.readline()))
            if self.server.client.add_tx(tx):
                self.wfile.write(format_object_for_transmission("SUCCESS"))
            else:
                self.wfile.write(format_object_for_transmission("FAILURE"))
        else:
            print("Unknown message type: {}".format(message))

    def get_message(self):
        return str(self.rfile.readline().strip(), "utf-8")

    def get_message_data(self):
        return data_from_request(self.rfile.readline())


class JoCoinListener():
    def __init__(self, client, listen_addr):
        self.server = socketserver.TCPServer(listen_addr, JoCoinServer)
        self.server.client = client

    def start(self):
        print("Starting JoCoin server")
        self.server.serve_forever()
