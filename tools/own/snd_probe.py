"""Read-only probe (sound per hero, 2026-11-18): at every snapshot frame print the game's 3D sound list and both listeners.

  python -I tools/own/snd_probe.py <testDir> <pinePort> <frame,...> <out.txt>

The list: head word 0x01E2AA80, next +28; a node: +0 position (x y z floats), +20 handle, +36 flags, +40 volume (s16, 0..16383,
written by the 3D routine 0x002BB5F8), +42 lowest volume, +44 pan (64 = middle), +46 object, +48 state, +49 kind.
Also: player 1's hero (0x00352400) and the twin (0x000F05CC) positions (+0x70), view 0's and view 1's eye (0x003A7F70 / 0x003A8000
+ 0x50), the view index 0x0033CC40, the two-view byte 0x0033CC44 and the own-screen word V_ON 0x000F6F04.
"""
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


def fl(b, o):
    return struct.unpack_from("<f", b, o)[0]


def vec(a):
    b = p.read(a, 12)
    return "(%.0f %.0f %.0f)" % (fl(b, 0), fl(b, 4), fl(b, 8))


t0 = time.time()
lines = []
seen = 0
while seen < len(frames) and time.time() - t0 < 1200.0:
    f = frames[seen]
    if not (test_dir / ("p1_f%06d.png" % f)).exists():
        time.sleep(0.02)
        continue
    seen += 1
    try:
        hero, twin = p.r32(0x00352400), p.r32(0x000F05CC)
        hp = vec(hero + 0x70) if 0x00100000 <= hero < 0x02000000 else "-"
        tp = vec(twin + 0x70) if 0x00100000 <= twin < 0x02000000 else "-"
        lines.append("f%d hero %s twin %s eye0 %s eye1 %s idx %d dual %d on %d areas %d" % (
            f, hp, tp, vec(0x003A7F70 + 0x50), vec(0x003A8000 + 0x50), p.r32(0x0033CC40), p.read(0x0033CC44, 1)[0],
            p.r32(0x000F6F04), p.r32(0x0034A400)))
        a = p.r32(0x01E2AA80)
        n = 0
        while 0x00100000 <= a < 0x02000000 and n < 80:
            b = p.read(a, 52)
            vol, low, pan, obj = struct.unpack_from("<hhhH", b, 40)
            lines.append("f%d  node %08X pos (%.0f %.0f %.0f) id %08X flags %X vol %d low %d pan %d obj %04X state %d kind %d" % (
                f, a, fl(b, 0), fl(b, 4), fl(b, 8), struct.unpack_from("<I", b, 20)[0], struct.unpack_from("<I", b, 36)[0],
                vol, low, pan, obj, b[48], b[49]))
            a = struct.unpack_from("<I", b, 28)[0]
            n += 1
    except Exception as e:  # noqa: BLE001
        lines.append("f%d read failed: %r" % (f, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
