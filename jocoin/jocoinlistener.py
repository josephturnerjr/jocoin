import socketserver


class JoCoinServer(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data, self.server.client.chain.length())
        self.wfile.write(self.data.upper())


class JoCoinListener():
    HOST = "localhost"
    PORT = 9999
    def __init__(self, client):
        self.server = socketserver.TCPServer((self.HOST, self.PORT), JoCoinServer)
        self.server.client = client

    def start(self):
        print("Starting JoCoin server")
        self.server.serve_forever()
