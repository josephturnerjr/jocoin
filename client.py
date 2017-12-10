import optparse
import json
import sys
import jocoin.network as jnw
from jocoin.tx import TxInput, TxOutput
from jocoin.user import make_tx


def read_keyfile(fn):
    with open(fn) as f:
        return json.loads(f.read())

if __name__ == "__main__":
    usage = """usage: %prog [options] <command> [<args>]

Available commands:
    balance <keyfile>: Get the balance for the account linked to the key in <keyfile>
    inputs <keyfile>: Get the available inputs for the account linked to the key in <keyfile>
    transfer <your keyfile> <to_keyfile> <amount>: Transfer <amount> from your account to <to_keyfile>'s account"""

    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-H", "--host", help="server address", dest="server_addr", default="localhost")
    parser.add_option("-p", "--port", help="server port", type="int", dest="server_port", default=9999)

    (options, args) = parser.parse_args()

    print(args)

    if not args:
        parser.print_help()
        sys.exit()

    command = args[0]
    server_addr = (options.server_addr, options.server_port)

    if command == "balance":
        if len(args) != 2:
            parser.print_help()
            sys.exit()
        key = read_keyfile(args[1])
        print(jnw.request_balance(server_addr, key['pubkey']))
    if command == "inputs":
        if len(args) != 2:
            parser.print_help()
            sys.exit()
        key = read_keyfile(args[1])
        print([(TxInput.from_json(x), y) for x, y in jnw.request_inputs(server_addr, key['pubkey'])])
    elif command == "transfer":
        if len(args) != 4:
            parser.print_help()
            sys.exit()
        from_key = read_keyfile(args[1])
        to_key = read_keyfile(args[2])
        amount = float(args[3])
        inputs = [(TxInput.from_json(x), y) for x, y in jnw.request_inputs(server_addr, from_key['pubkey'])]
        outputs = [TxOutput(to_key['pubkey'], amount)]
        tx = make_tx(inputs, from_key['privkey'], from_key['pubkey'], outputs)
        print(jnw.request_transfer(server_addr, tx))
