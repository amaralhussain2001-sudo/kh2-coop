"""Read-only probe (ninth round, job 3): at each snapshot frame, EVERY OBJECT OF THE ROOM THAT HAS AN HP RECORD:
its address, object number and model name (from its object entry), the address of its unit slot (object + 0x48C),
HP / most HP, its action word, its place. For finding a boss's HP record, so that a test kit can write it once
(tools/own/make_once.py) and push a fight into a later part.
The object list: head 0x01D48DA0, next at object + 2228.
  python -I tools/own/enemy_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x0034E948), p.r32(0x000F05CC)
        lines.append("f%d engine's player %08X twin %08X story event %08X camera hold %08X" % (
            fr, h1, h2, p.r32(0x0035037C), p.r32(0x0033CC38)))
        a, n = p.r32(0x01D48DA0), 0
        while ok(a) and n < 400:
            slot = p.r32(a + 0x48C)
            e = p.r32(a + 8)
            if ok(slot) and ok(e):
                hp, top = struct.unpack("<2i", p.read(slot, 8))
                x, y, z = struct.unpack("<3f", p.read(a + 0x70, 12))
                lines.append("  f%d obj %08X %04X %-16s slot %08X HP %d/%d act %04X held %d at (%.0f, %.0f, %.0f)" % (
                    fr, a, p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20)), slot, hp, top, p.r32(a + 0x154) & 0xFFFF,
                    (p.r32(a + 0x160) >> 14) & 1, x, y, z))
            a = p.r32(a + 2228)
            n += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
