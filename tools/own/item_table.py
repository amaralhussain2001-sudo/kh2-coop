"""Read-only: the game's item table (03system.bin, BAR entry "item") of the original disc's extracted files.
Prints id, type, the inventory slot and the raw words, for the item ids given (default: magic and Keyblades).
Layout (HYPOTHESIS, checked against the known magic places below): header (version, count), then 0x18-byte
entries: id u16, type u8, flag0 u8, flag1 u8, rank u8, stat u16, name u16, desc u16, buy u16, sell u16,
command u16, slot u16, picture u16, icon1 u8, icon2 u8.
The test kits put Fire / Blizzard / Thunder / Cure at save + 0x3594..0x3597 (lane G, VERIFIED in a game).
  python -I tools/own/item_table.py [id ...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "extract" / "kh2" / "03system.bin").read_bytes()
assert d[:4] == b"BAR\x01", d[:4]
n = struct.unpack_from("<I", d, 4)[0]
ents = {}
for i in range(n):
    typ, name, off, size = struct.unpack_from("<I4sII", d, 16 + 16 * i)
    ents[name.rstrip(b"\0").decode("ascii", "replace")] = (typ, off, size)
print("bar entries:", ", ".join(sorted(ents)))
typ, off, size = ents["item"]
ver, cnt = struct.unpack_from("<II", d, off)
print("item table: version %d, %d entries, size %d" % (ver, cnt, size))
want = [int(x, 0) for x in sys.argv[1:]] or [21, 22, 23, 24, 41, 42, 43, 1, 2]
for k in range(cnt):
    e = d[off + 8 + 0x18 * k: off + 8 + 0x18 * (k + 1)]
    iid, ityp, f0, f1, rank, stat, nm, ds, buy, sell, cmd, slot, pic, i1, i2 = struct.unpack("<HBBBBHHHHHHHHBB", e)
    if iid in want:
        print("id %3d (0x%03X) type %2d rank %d stat %3d slot %3d (0x%03X) -> save + 0x%04X | buy %d sell %d cmd %d" % (
            iid, iid, ityp, rank, stat, slot, slot, 0x3580 + slot, buy, sell, cmd))
