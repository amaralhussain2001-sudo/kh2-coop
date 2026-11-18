"""Read-only probe for the eighty-sixth glue --hullgauges (part 152): at each snapshot frame the score, both ships' hulls, the
second gauge G2 (0x000D4B00: class, state +212, its pictures), V_WORK / V_POOLN / V_DIG2 (0x000D4C00..), and the places
(+356/+360) of the gauges' pictures +4/+8/+12/+16/+24/+164 and the bars +172/+192 (+4/+8) of G2 and of the game's gauge G1 (found
once by its class word 0x01F817C8 in 0x01F18000 .. 0x02000000, G2 excluded). Before the flight module is in memory: how many words
of 0x000C0000 .. 0x000D4C10 are not zero (pool B must be free memory).
  python -I tools/own/hg_probe.py <testDir> <pinePort> <frame,...> <out.txt>"""
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
t0, lines, g1 = time.time(), [], None


def nonzero(lo, hi):
    n = 0
    for a in range(lo, hi, 0x1000):
        b = p.read(a, min(0x1000, hi - a))
        n += sum(1 for k in range(0, len(b), 4) if b[k:k + 4] != b"\0\0\0\0")
    return n


def places(g):
    s = []
    for k in (4, 8, 12, 16, 24, 164, 168):
        pic = p.r32(g + k)
        if 0x00080000 <= pic < 0x02000000:
            x, y = struct.unpack("<2i", p.read(pic + 356, 8))
            s.append("+%d(%d,%d)" % (k, x, y))
        else:
            s.append("+%d-" % k)
    for k in (172, 192):
        x, y = struct.unpack("<2i", p.read(g + k + 4, 8))
        s.append("bar%d(%d,%d)" % (k, x, y))
    npic = sum(1 for k in range(4, 172, 4) if p.r32(g + k))
    return "state %d pics %d %s" % (p.r32(g + 212), npic, " ".join(s))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 1500:
        time.sleep(0.05)
    try:
        row = "f%d mode %d" % (fr, p.r32(0x0032BA24))
        if p.r16(0x01F18014) == 0x636A:
            ship = p.r32(0x01F7DE44)
            s1, s2 = struct.unpack("<2I", p.read(0x000F2600, 8))
            row += " | score %d" % p.r32(0x01F8039C)
            if 0x01000000 <= s1 < 0x02000000:
                row += " | ship1 hull %.0f st %d%s" % (p.rf(s1 + 0x4AC), p.r32(s1 + 0x50C), "" if s1 == ship else " (NOT THE GAME'S)")
            if 0x01000000 <= s2 < 0x02000000:
                row += " | ship2 hull %.0f st %d" % (p.rf(s2 + 0x4AC), p.r32(s2 + 0x50C))
            work, pooln, dig2 = struct.unpack("<3I", p.read(0x000D4C00, 12))
            row += " | G2 class %08X work %d pool %d dig2 %08X %s" % (p.r32(0x000D4B00), work, pooln, dig2, places(0x000D4B00))
            if g1 is None:
                for a in range(0x01F18000, 0x02000000, 0x4000):
                    b = p.read(a, 0x4000)
                    for k in range(0, len(b), 4):
                        if b[k:k + 4] == b"\xC8\x17\xF8\x01" and p.r32(a + k + 212) in (0, 1, 2, 3) and a + k != 0x000D4B00:
                            g1 = a + k
                            break
                    if g1:
                        break
            if g1:
                row += " | G1 %08X %s" % (g1, places(g1))
        else:
            row += " | no flight module | nonzero words 0x000C0000..0x000D0000 %d, pool B and G2 0x000D0000..0x000D4C10 %d" % (
                nonzero(0x000C0000, 0x000D0000), nonzero(0x000D0000, 0x000D4C10))
        lines.append(row)
    except Exception as e:  # noqa: BLE001
        lines.append("f%d: read failed: %r" % (fr, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
