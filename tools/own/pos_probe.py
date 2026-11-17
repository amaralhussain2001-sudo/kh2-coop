"""Read-only probe: at each snapshot frame the place (x, y, z) of both heroes, their action word and the distance
between them; and the place of up to three points given as POINTS="x:z,x:z" (flat distance of each hero to them).
  python -I tools/own/pos_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import math
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
points = [tuple(float(v) for v in q.split(":")) for q in os.environ.get("POINTS", "").split(",") if q]
p = Pine(port, wait=120)
t0 = time.time()
lines = []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        row = ["f%d L%d" % (fr, p.read(0x000F6F00, 1)[0])]
        for nm, ptr in (("P1", 0x0034E948), ("P2", 0x000F05CC)):
            o = p.r32(ptr)
            if not o:
                row.append("%s none" % nm)
                continue
            x, y, z = struct.unpack("<3f", p.read(o + 0x70, 12))
            row.append("%s (%.0f, %.0f, %.0f) act %02X" % (nm, x, y, z, p.r32(o + 0x154) & 0xFFFF)
                       + "".join(" d%d %.0f" % (i, math.hypot(x - px, z - pz)) for i, (px, pz) in enumerate(points)))
        lines.append(" | ".join(row))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
