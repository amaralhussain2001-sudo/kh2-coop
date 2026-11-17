"""Read-only probe: sweep_probe.py's line for each snapshot frame, plus memory words (for the small recorder kits).
  RANGES=000F1FC0:20,0032F0D2:4 python -I tools/own/sweepm_probe.py <testDir> <pinePort> <frame,...> <out.txt>
RANGES = start:length pairs (hex, length a multiple of 4); printed as 32-bit words after " | ".
CHAINS = pointer chains like memdump_probe.py: 0034E948+48C@180:8 = 8 bytes from offset 0x180 of the object that
the word at (word at 0034E948) + 48C points to."""
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
ranges = [tuple(int(v, 16) for v in r.split(":")) for r in os.environ.get("RANGES", "").split(",") if r]
chains = [c for c in os.environ.get("CHAINS", "").split(",") if c]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "200"))


def ok(a):
    return 0x00080000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return "none"
    s = p.r32(o + 0x48C)
    if not ok(s):
        return "noslot"
    return "%d/%d a%02X" % (p.r32(s), p.r32(s + 4), p.r32(o + 0x154) & 0xFFFF)


def words(a, n):
    return " ".join("%08X" % w for w in struct.unpack("<%dI" % (n // 4), p.read(a, n)))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        s = "f%d room %04X btl %d L%d P1 %s P2 %s msn %d go %d" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r8(0x000F6F00), hero(p.r32(0x0034E948)),
            hero(p.r32(0x000F05CC)), 1 if p.r32(0x01D49320) else 0, 1 if p.r32(0x00350DF0) else 0)
        for a, n in ranges:
            s += " | %08X: %s" % (a, words(a, n))
        for c in chains:
            path, n = c.split(":")
            path, _, skip = path.partition("@")
            steps = path.split("+")
            a = p.r32(int(steps[0], 16))
            for st in steps[1:]:
                a = p.r32(a + int(st, 16)) if ok(a) else 0
            s += " | %s: %s" % (c, words(a + (int(skip, 16) if skip else 0), int(n, 16)) if ok(a) else "no object")
        lines.append(s)
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail" % fr)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
