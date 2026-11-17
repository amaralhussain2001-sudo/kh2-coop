"""Read-only probe: where does memory hold a hero's position? At each snapshot frame the twin's and player 1's
position (object +0x70) is read, then the object heap is searched for the same three floats in a row.
  python -I tools/own/posfind_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
LO, HI = 0x01800000, 0x01D80000
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        for nm, o in (("P1", p.r32(0x0034E948)), ("P2", p.r32(0x000F05CC))):
            if not o:
                continue
            key = p.read(o + 0x70, 12)
            ram = p.read(LO, HI - LO)
            again = p.read(o + 0x70, 12)
            hits = []
            i = ram.find(key)
            while i >= 0:
                if i % 4 == 0:
                    hits.append(LO + i)
                i = ram.find(key, i + 4)
            lines.append("frame %d %s %08X at %s%s: %s" % (
                fr, nm, o, " ".join("%.1f" % v for v in struct.unpack("<3f", key)), "" if again == key else " (moved while reading)",
                " ".join(("+%X" % (a - o)) if o <= a < o + 0x1000 else "%08X" % a for a in hits)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
