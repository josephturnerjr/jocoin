from .tx import InvalidTransactionException, Tx, TxOutput
from .signature import create_signature


def find_inputs(all_inputs, out_total):
    sum_total = 0.0
    inputs = []
    for i, amt in all_inputs:
        if sum_total < out_total:
            inputs.append(i)
            sum_total += amt
        else:
            break
    if sum_total < out_total:
        raise InvalidTransactionException("Requested amount is larger than available funds")
    return (inputs, sum_total - out_total)

def make_tx(all_inputs, privkey, pubkey, outputs):
    return make_tx_with_fee(all_inputs, privkey, pubkey, outputs, 0.0)

def make_tx_with_fee(all_inputs, privkey, pubkey, outputs, fee):
    out_total = fee + sum(x.amount for x in outputs)
    inputs, remainder = find_inputs(all_inputs, out_total)
    if remainder > 0.0:
        outputs.append(TxOutput(pubkey, remainder))
    sig = create_signature((inputs, outputs), privkey)
    return Tx(pubkey, sig, inputs, outputs)
