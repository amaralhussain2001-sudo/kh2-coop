"""Read-only probe (ninth round, the sixty-eighth glue): WHERE A CONTROLLER'S STICK LIVES. At each snapshot frame, for both
logical controller records (0x0034D6C0 and + 0x60): the held word, the words + 0x20 .. + 0x5F, and the same words
of the pad structure the record points to (+ 0x44); the two heroes' action and held bit.
  python -I tools/own/pads_probe2.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def words(a, n):
    return " ".join("%08X" % w for w in struct.unpack("<%dI" % n, p.read(a, 4 * n)))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        row = ["f%d" % fr]
        for k, a in ((0, 0x0034D6C0), (1, 0x0034D720)):
            pad = p.r32(a + 0x44)
            row.append("  rec%d held %s | +20: %s" % (k, words(a, 2), words(a + 0x20, 16)))
            if ok(pad):
                row.append("  rec%d pad %08X | +00: %s | +20: %s" % (k, pad, words(pad, 8), words(pad + 0x20, 16)))
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        for who, a in (("P1", h1), ("P2", h2)):
            if ok(a):
                row.append("  %s %08X a%X held %d control word B38 %08X" % (who, a, p.r32(a + 0x154) & 0xFFFF, (p.r32(a + 0x160) >> 14) & 1, p.r32(a + 0xB38)))
        lines.append("\n".join(row))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
