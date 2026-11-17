"""Read-only probe for the Mail Delivery end test: at each snapshot frame the room, the view layout, the mission's
counters, the munny, both heroes (position, board mode, control object's open menu id) and the letter recipients
(found once near their spawn points: position and the flag word +0x0C).
  python -I tools/own/mail_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 900]"""
import math
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
REC = {1: (740.3, 550.0, -1458.5), 2: (-141.4, -407.9, 1760.5), 3: (115.6, 300.0, -872.2),
       4: (-906.2, -200.5, 232.6), 5: (2022.9, 26.0, -1114.6)}
p = Pine(port, wait=120)
t0 = time.time()
lines, recs = [], {}


def pos(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12))


def hero(nm, o, ctl):
    if not o:
        return "%s none" % nm
    menu = p.r32(ctl + 0x9E8)
    return "%s %08X at %s board %d menu %d" % (nm, o, " ".join("%.0f" % v for v in pos(o)), p.r32(o + 0xB70), p.r32(menu) if menu else -1)


for k, fr in enumerate(frames):
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        lines.append("frame %d room %04X layout %d count %d %d munny %d | %s | %s" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.read(0x000F6F00, 1)[0], p.r32(0x01D48EFC), p.r32(0x01D48EFC + 0x38),
            p.r32(0x0032DF70), hero("P1", pl, 0x01C5F530), hero("P2", tw, 0x000F1000)))
        if k == 0:
            ram = p.read(0x01800000, 0x00500000)
            n = len(ram) // 4
            words = struct.unpack("<%dI" % n, ram)
            for i in range(0, n - 0x130, 4):
                w = words[i]
                if not 0x00340000 <= w < 0x00370000:
                    continue
                x, y, z = struct.unpack_from("<3f", ram, 4 * i + 0x70)
                if math.isnan(x) or math.isnan(y) or math.isnan(z):
                    continue
                for r, (rx, ry, rz) in REC.items():
                    if abs(x - rx) < 30 and abs(y - ry) < 60 and abs(z - rz) < 30 and r not in recs:
                        recs[r] = 0x01800000 + 4 * i
        for r in sorted(recs):
            o = recs[r]
            lines.append("   recipient %d: %08X class %08X at %s flags %08X" % (r, o, p.r32(o), " ".join("%.0f" % v for v in pos(o)), p.r32(o + 0x0C)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
