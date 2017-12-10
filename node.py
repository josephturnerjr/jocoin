import sys
import json
from jocoin.client import Client
from jocoin.crypto import gen_keys
from optparse import OptionParser

def read_keyfile(fn):
    with open(fn) as f:
        return json.loads(f.read())

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-k", "--keyfile", dest="keyfile",
                      help="public/private keyfile", metavar="FILE")
    parser.add_option("-H", "--host", help="server address", dest="server_addr", default="localhost")
    parser.add_option("-p", "--port", help="server port", type="int", dest="server_port", default=9999)

    (options, args) = parser.parse_args()

    print(options, args)

    if options.keyfile:
        keys = read_keyfile(options.keyfile)
    else:
        print("TEST MODE: using random keys")
        keys = gen_keys()

    listen_addr = (options.server_addr, options.server_port)
    
    if args:
        peer_addr, peer_port = args
        peers = [(peer_addr, int(peer_port))]
    else:
        peers = []
    c = Client(tuple(keys["pubkey"]), tuple(keys["privkey"]), peers, listen_addr)
    c.start()
