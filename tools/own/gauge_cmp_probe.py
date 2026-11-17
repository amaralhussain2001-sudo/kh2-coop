"""Read-only probe: the two big player gauges (player 1's = the object of class 0x0034A920 among the HUD's gauge
pointers 0x003485E0.., player 2's = [0x000F7F20]) compared part by part at each snapshot frame. An embedded part
is found by its class word (0x00347E00..0x00348700 at a word place where both objects hold the same value); the
line shows the part's offset, class, flag word (+12) and sequence numbers (+388, +392) in both gauges when they
differ.
  python -I tools/own/gauge_cmp_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
SIZE = 0x3D00
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        g2 = p.r32(0x000F7F20)
        g1 = 0
        for a in range(0x003485E0, 0x00348640, 4):
            o = p.r32(a)
            if 0x00100000 <= o < 0x02000000 and p.r32(o) == 0x0034A920:
                g1 = o
                break
        lines.append("frame %d gauge1 %08X gauge2 %08X" % (fr, g1, g2))
        if not g1 or not g2:
            continue
        d1 = struct.unpack("<%dI" % (SIZE // 4), p.read(g1, SIZE))
        d2 = struct.unpack("<%dI" % (SIZE // 4), p.read(g2, SIZE))
        for i in range(1, SIZE // 4 - 100):
            if d1[i] == d2[i] and 0x00347E00 <= d1[i] < 0x00348700:
                f1, f2 = d1[i + 3], d2[i + 3]
                s1, s2 = d1[i + 97], d2[i + 97]
                if f1 != f2 or s1 != s2:
                    lines.append("   part +%04X class %08X | P1 flags %08X seq %d next %d | P2 flags %08X seq %d next %d" % (
                        4 * i, d1[i], f1, s1, d1[i + 98] - (1 << 32 if d1[i + 98] >> 31 else 0), f2, s2, d2[i + 98] - (1 << 32 if d2[i + 98] >> 31 else 0)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
