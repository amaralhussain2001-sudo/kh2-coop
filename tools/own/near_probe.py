"""Read-only probe: find the game objects standing near the twin at the first frame, then follow them.

  python -I tools/own/near_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [radius]

An "object" here = an aligned place in 0x01000000-0x01FFFFFF whose first word looks like a class table in the
game program (0x00340000-0x0036FFFF) and whose +0x70..+0x7B are three sane floats (the engine's position place).
First frame: lists the objects within <radius> (default 200) of the twin (0x000F05CC) that are not a hero.
Later frames: position, the flag words at +0x08..+0x14, +0x1C, and 12 words of the script work area if the
object has a script context (+0x484).
"""
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
radius = float(sys.argv[5]) if len(sys.argv) > 5 else 200.0
p = Pine(port, wait=120)
t0 = time.time()
lines, objs = [], []


def pos_of(a):
    return struct.unpack("<3f", p.read(a + 0x70, 12))


for k, fr in enumerate(frames):
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 600:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        hero, twin = p.r32(0x00348638), p.r32(0x000F05CC)
        if k == 0:
            tx, ty, tz = pos_of(twin)
            lines.append("frame %d: twin %08X at (%.1f %.1f %.1f), hero %08X at (%.1f %.1f %.1f)" % ((fr, twin, tx, ty, tz, hero) + pos_of(hero)))
            ram = p.read(0x01000000, 0x01000000)
            n = len(ram) // 4
            words = struct.unpack("<%dI" % n, ram)
            for i in range(0, n - 0x130, 4):          # objects are 16-byte aligned
                w = words[i]
                if not 0x00340000 <= w < 0x00370000:
                    continue
                x, y, z = struct.unpack_from("<3f", ram, 4 * i + 0x70)
                if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6) or (x == 0.0 and y == 0.0 and z == 0.0):
                    continue
                if math.isnan(x) or math.isnan(y) or math.isnan(z):
                    continue
                d = math.sqrt((x - tx) ** 2 + (z - tz) ** 2)
                a = 0x01000000 + 4 * i
                if d <= radius and abs(y - ty) < 2000 and a not in (hero, twin):
                    objs.append(a)
                    lines.append("  candidate %08X class %08X at (%.1f %.1f %.1f), %.0f from the twin" % (a, w, x, y, z, d))
        lines.append("=== frame %d" % fr)
        for a in objs:
            b = p.read(a, 0x4A0)
            cls = struct.unpack_from("<I", b, 0)[0]
            x, y, z = struct.unpack_from("<3f", b, 0x70)
            f = struct.unpack_from("<4I", b, 0x08)
            ctx = struct.unpack_from("<I", b, 0x484)[0]
            work = ""
            if 0x01000000 <= ctx < 0x02000000:
                c = struct.unpack("<16I", p.read(ctx, 64))
                wp = next((v for v in c if 0x01000000 <= v < 0x02000000), 0)
                work = " ctx %08X: %s" % (ctx, " ".join("%X" % v for v in c[:10]))
                if wp:
                    wv = struct.unpack("<8I", p.read(wp, 32))
                    work += " | work %08X: %s" % (wp, " ".join("%X" % v for v in wv))
                    if 0x01000000 <= wv[0] < 0x02000000:      # W0 = the script's own record of its object
                        ov = struct.unpack("<12i", p.read(wv[0], 48))
                        work += " | W0 -> %08X: %s" % (wv[0], " ".join("%d" % v for v in ov))
            lines.append("  %08X class %08X pos (%.1f %.1f %.1f) +8 %08X %08X %08X %08X%s" % ((a, cls, x, y, z) + f + (work,)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
