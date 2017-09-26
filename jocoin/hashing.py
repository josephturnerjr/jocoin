import hashlib

from .serialization import serialize


def hash_(obj):
    # Keep it simple: return (as integer) the sha256 hash of the 
    #   serialization of the object
    ser = serialize(obj).encode('utf-8')
    return int.from_bytes(hashlib.sha256(ser).digest(), 'big')
