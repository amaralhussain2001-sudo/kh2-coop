"""Read-only probe: polls the camera hold and both heroes' "in a scripted move" bit (object +0x160, 0x4000) all
through a run; one line per change, with the heroes' heights (to see who is in the air).
  python -I tools/own/flag_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 900]"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 900.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []
final = test_dir / ("p1_f%06d.png" % frames[-1])
last = None
seen = 0
while not final.exists() and time.time() - t0 < timeout:
    try:
        hold = p.r32(0x0033CC38)
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        a = p.r32(pl + 0x160) if pl else 0
        b = p.r32(tw + 0x160) if tw else 0
        key = (hold, (a >> 14) & 1, (b >> 14) & 1, pl, tw)
        while seen < len(frames) and (test_dir / ("p1_f%06d.png" % frames[seen])).exists():
            lines.append("-- snapshot %d" % frames[seen])
            seen += 1
        if key != last:
            last = key
            ya = struct.unpack("<f", p.read(pl + 0x74, 4))[0] if pl else 0
            yb = struct.unpack("<f", p.read(tw + 0x74, 4))[0] if tw else 0
            lines.append("%7.2fs hold %d | P1 %08X +160 %08X y %.0f | TW %08X +160 %08X y %.0f" % (time.time() - t0, hold, pl, a, ya, tw, b, yb))
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
        continue
    time.sleep(0.003)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
