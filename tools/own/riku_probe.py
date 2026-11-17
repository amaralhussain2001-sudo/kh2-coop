"""Read-only probe (ninth round, job 3): WHO STEERS RIKU while the last Xemnas holds the heroes. At each snapshot frame:
the engine's player (0x0034E948), player 1's hero (0x00352400), the twin (0x000F05CC), and for both heroes, Riku
(object 0x08D1) and the Xemnas objects (0x081F / 0x09CA): the action, the held bit, "has a hooked script", HP, place.
  python -I tools/own/riku_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
NAMES = {0x08D1: "Riku", 0x081F: "Xemnas", 0x09CA: "Xemnas"}


def ok(a):
    return 0x00080000 <= a < 0x02000000


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        eng, h1, h2 = p.r32(0x0034E948), p.r32(0x00352400), p.r32(0x000F05CC)
        row = "f%d engine's player %s" % (fr, "P1" if eng == h1 else "P2" if eng == h2 else "%08X" % eng)
        a, n = p.r32(0x01D48DA0), 0
        while ok(a) and n < 400:
            e = p.r32(a + 8)
            num = p.r32(e) & 0xFFFF if ok(e) else 0
            who = "P1" if a == h1 else "P2" if a == h2 else NAMES.get(num)
            if who:
                slot = p.r32(a + 0x48C)
                hp = struct.unpack("<i", p.read(slot, 4))[0] if ok(slot) else -1
                x, y, z = struct.unpack("<3f", p.read(a + 0x70, 12))
                row += " | %s a%X held %d hook %d HP %d (%.0f, %.0f, %.0f)" % (
                    who, p.r32(a + 0x154) & 0xFFFF, (p.r32(a + 0x160) >> 14) & 1, 1 if p.r32(a + 0xAEC) else 0, hp, x, y, z)
            a = p.r32(a + 2228)
            n += 1
        lines.append(row)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
