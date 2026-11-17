"""Read-only probe (ninth round, the sixty-eighth glue): at each snapshot frame the two logical controller records
(0x0034D6C0 and + 0x60: held word, left stick x / y / strength), the sixty-eighth glue's values (0x000E7F80 flag,
0x7F88 controller 2's own held word, 0x7F90 held by either), the twenty-sixth glue's flag (0x000F2638), the
sixty-fifth glue's pair (0x000E7EA0 .. 0x7EBC), and both heroes' and Riku's action / held bit / place.
  python -I tools/own/pads_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def rec(a):
    held = struct.unpack("<Q", p.read(a, 8))[0]
    x, y, _z, s = struct.unpack("<4f", p.read(a + 0x20, 16))
    return "held %016X stick (%.2f, %.2f) strength %.2f [%08X]" % (held, x, y, s, p.r32(a + 0x2C))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        row = "f%d rec0 %s | rec1 %s | glue 68: flag %d own2 %016X either %016X | gm flag %d | pair %s" % (
            fr, rec(0x0034D6C0), rec(0x0034D720), p.r32(0x000E7F80), struct.unpack("<Q", p.read(0x000E7F88, 8))[0],
            struct.unpack("<Q", p.read(0x000E7F90, 8))[0], p.r32(0x000F2638),
            " ".join("%08X" % w for w in struct.unpack("<8I", p.read(0x000E7EA0, 32))))
        for who, a in (("P1", h1), ("P2", h2)):
            if ok(a):
                x, y, z = struct.unpack("<3f", p.read(a + 0x70, 12))
                row += " | %s %08X a%X held %d (%.0f, %.0f, %.0f)" % (who, a, p.r32(a + 0x154) & 0xFFFF, (p.r32(a + 0x160) >> 14) & 1, x, y, z)
        lines.append(row)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
