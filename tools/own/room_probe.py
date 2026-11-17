"""Read-only probe: room number, battle byte and both heroes' HP at given snapshot frames (one line each).
  python -I tools/own/room_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
"""
import pathlib
import sys
import time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
p = Pine(port, wait=120)
t0, lines = time.time(), []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 600:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: no screenshot" % fr)
        break
    try:
        lines.append("frame %d room %04X battle %02X layout %d two-view flag %d" % (fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r32(0x000F6F00) & 0xFF, p.r32(0x0033CC44) & 0xFF))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(sys.argv[4]).write_text("\n".join(lines) + "\n", encoding="utf-8")
