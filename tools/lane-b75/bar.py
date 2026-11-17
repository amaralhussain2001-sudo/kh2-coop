"""Minimal reader for the game's BAR container (used by .mdlx, 00battle.bin and others). Lane B75.

Header: 'BAR\\x01', int32 count, 8 bytes; then count entries of 16 bytes:
u16 type, u16 duplicate, char[4] name, u32 offset, u32 size. (Checked against OpenKH's listing of the same files.)
"""
import struct

TYPE_LIST = 2
TYPE_BDX = 3


def entries(blob):
    if blob[:3] != b"BAR":
        raise ValueError("not a BAR file")
    count = struct.unpack_from("<i", blob, 4)[0]
    out = []
    for i in range(count):
        typ, dup, name, off, size = struct.unpack_from("<HH4sII", blob, 16 + 16 * i)
        out.append({"type": typ, "dup": dup, "name": name.rstrip(b"\0").decode("ascii", "replace"),
                    "offset": off, "size": size})
    return out


def find(blob, name, typ=None):
    for e in entries(blob):
        if e["name"] == name and (typ is None or e["type"] == typ):
            return e
    raise KeyError(name)
