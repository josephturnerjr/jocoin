import socket
import socketserver
from .serialization import serialize, deserialize

def format_obj_for_transmission(o):
    return format_string_for_transmission(serialize(o))

def format_string_for_transmission(s):
    return bytes(s + "\n", "utf-8")

def gossip_with(peer, raw_data):
    serialized = serialize(raw_data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(peer)
        sock.sendall(format_string_for_transmission(serialized))
        serialized_received = readline(sock)
    finally:
        sock.close()

    received = deserialize(serialized_received)
    return received

def readline(sock, bufsize=4096):
    buf = ''
    data = True
    while data:
        data = str(sock.recv(bufsize), "utf-8")
        buf += data
        if '\n' in buf:
            return buf.splitlines()[0]

class JoCoinServer(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        serialized = serialize(self.server.client.get_all_state())
        self.wfile.write(format_string_for_transmission(serialized))
        self.server.client.handle_peer_data(deserialize(data))


class JoCoinListener():
    def __init__(self, client, listen_addr):
        self.server = socketserver.TCPServer(listen_addr, JoCoinServer)
        self.server.client = client

    def start(self):
        print("Starting JoCoin server")
        self.server.serve_forever()
