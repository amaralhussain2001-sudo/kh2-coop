"""Read-only probe (ninth round): the party friends and the slot number each one carries.
Read: the friend's follow routine 0x0010E810 takes the friend's slot number (object + 0xB70; 1 or 2, set by
0x00111ED4 and 0x0010BA40) as an index into the table 0x00341720 (16 bytes each). A wild number there gives the
fault lines "pc 0x0010E8AC". At each snapshot frame: the party table 0x00341708 (the engine's player and two
friends) and, for EVERY object of the room whose class is the friend's (the first word of the object = the
class table 0x00345C08), its address, name, the words at + 0xB6C and + 0xB70 and its action.
  python -I tools/own/friend_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def ok(a):
    return 0x00080000 <= a < 0x02000000


def text_of(raw):
    best, cur = b"", b""
    for b in raw:
        if 0x20 <= b < 0x7F:
            cur += bytes([b])
        else:
            if len(cur) > len(best):
                best = cur
            cur = b""
    if len(cur) > len(best):
        best = cur
    return best.decode("ascii", "replace") if len(best) >= 4 else ""


def name(o):
    e = p.r32(o + 8)
    return "%04X %s" % (p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20))) if ok(e) else "?"


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        tab = struct.unpack("<3I", p.read(0x00341708, 12))
        lines.append("f%d party table %08X %08X %08X | engine's player %08X twin %08X" % (
            fr, tab[0], tab[1], tab[2], p.r32(0x0034E948), p.r32(0x000F05CC)))
        a, n = p.r32(0x01D48DA0), 0
        while ok(a) and n < 400:
            cls = p.r32(a)
            if cls == 0x00345C08 or a in tab[1:]:
                lines.append("  f%d %s %08X %-22s class %08X +B6C %08X +B70 %08X action %04X" % (
                    fr, "FRIEND" if cls == 0x00345C08 else "in the table", a, name(a), cls, p.r32(a + 0xB6C), p.r32(a + 0xB70),
                    p.r32(a + 0x154) & 0xFFFF))
            a = p.r32(a + 2228)
            n += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
