import json
from jocoin.crypto import gen_keys

if __name__ == "__main__":
    print(json.dumps(gen_keys()))
