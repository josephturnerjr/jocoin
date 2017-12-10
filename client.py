import json
from jocoin.network import request_balance


def read_keyfile(fn):
    with open(fn) as f:
        return json.loads(f.read())

if __name__ == "__main__":
    print(request_balance(('localhost', 9999), read_keyfile('jt.key')['pubkey']))
