import uhashlib as hashlib
import ubinascii

SHA256 = 0

_hash_map = {SHA256: hashlib.sha256}


def bytes_to_long(s):
    n = 0
    for b in s:
        n = (n << 8) | b
    return n


def long_to_bytes(n):
    _list = list()
    x = 0
    off = 0
    while x != n:
        byte = (n >> off) & 0xFF
        hexbyte = ubinascii.unhexlify("{0:0>2}".format(str(hex(byte))[2:]))
        _list.append(hexbyte)
        x = x | (byte << off)
        off += 8
    _list.reverse()
    return b''.join(_list)


def test():
    hash_class = _hash_map[SHA256]
    S = 4185037603
    K = hash_class(long_to_bytes(S)).digest()
    print(K)
