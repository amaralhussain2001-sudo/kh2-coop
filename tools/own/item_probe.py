"""(heal_probe.py + the helpers' item places: Donald's block 0x0032E134, Goofy's 0x0032E248; count byte +0x12,
eight places of 2 bytes at +0x34; and the item stock byte of the Potion, save + 0x3580 is NOT read.)
Read-only probe for the "whom do the helpers heal" tests: at each snapshot frame both heroes and the two
helpers of the party table (0x00348638): HP / most HP, MP / most MP, the action word (+0x154), the distance to
each hero; and Donald's last ability place in the save data.
  python -I tools/own/heal_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import math
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=120)
t0 = time.time()
lines = []


def pos(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12))


def who(nm, o, others):
    if not o:
        return "%s none" % nm
    s = p.r32(o + 0x48C)
    if not s:
        return "%s %08X no slot" % (nm, o)
    q = pos(o)
    d = " ".join("%.0f" % math.dist(q, pos(x)) for x in others if x)
    return "%s %08X slot %08X HP %d/%d MP %d/%d act %02X d %s" % (nm, o, s, p.r32(s), p.r32(s + 4), p.r32(s + 0x180), p.r32(s + 0x184), p.r32(o + 0x154) & 0xFFFF, d)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        party = struct.unpack("<3I", p.read(0x00348638, 12))
        lines.append("f%d L%d | %s | %s | %s | %s | save26F6 %04X" % (
            fr, p.read(0x000F6F00, 1)[0], who("P1", pl, ()), who("P2", tw, (pl,)), who("h1", party[1], (pl, tw)), who("h2", party[2], (pl, tw)),
            struct.unpack("<H", p.read(0x0032BB30 + 0x26F6, 2))[0]) + " | items D %d: %s G %d: %s" % (
            p.r8(0x0032E146), p.read(0x0032E168, 8).hex(), p.r8(0x0032E25A), p.read(0x0032E27C, 8).hex()))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
