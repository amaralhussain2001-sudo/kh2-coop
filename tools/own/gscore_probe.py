"""Read-only probe (ninth round, job 6): the Gummi flight's points for each player. At each snapshot frame, while the
flight module is loaded: the game's score (0x01F8039C), the kills (0x01F80856), PLAYER 2'S POINTS as the sixty-sixth
glue counts them (0x000E7EFC) and so player 1's (the score - player 2's), the credit and "fired last" words
(0x000E7EF8 / F4), both ships' hulls, the second score row's object (0x000E7F40: its frame picture, its state)
and the gauge mark (0x000E7F78).
  python -I tools/own/gscore_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
p = Pine(port, wait=120)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "900"))


def ok(a):
    return 0x00080000 <= a < 0x02000000


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    try:
        row = "f%d mode %d" % (fr, p.r32(0x0032BA24))
        if p.r16(0x01F18014) == 0x636A:
            score, p2 = p.r32(0x01F8039C), p.r32(0x000E7EFC)
            s1, s2 = p.r32(0x000F2600), p.r32(0x000F2604)
            row += " | score %d = player 1's %d + player 2's %d | kills %d | credit %d fired last %d | hull 1 %.0f hull 2 %.0f" % (
                score, score - p2, p2, p.r16(0x01F80856), p.r32(0x000E7EF8), p.r32(0x000E7EF4),
                p.rf(s1 + 0x4AC) if ok(s1) else -1, p.rf(s2 + 0x4AC) if ok(s2) else -1)
            row += " | row 2: picture %08X state %d mark %08X | jumps: %08X %08X %08X" % (
                p.r32(0x000E7F44), p.r32(0x000E7F68), p.r32(0x000E7F78), p.r32(0x01F1EE00), p.r32(0x01F536D0), p.r32(0x01F4DE90))
            row += " | own places given %d" % p.r32(0x000E7F98)
        if p.r16(0x01F18014) == 0x636A:
            def place(pic):
                return "(%d, %d)" % struct.unpack("<2i", p.read(pic + 356, 8)) if ok(pic) else "-"
            row += " | places: row 2 digits %s .. %s, mark %s, gauge noted (%d, %d)" % (
                place(p.r32(0x000E7F48)), place(p.r32(0x000E7F60)), place(p.r32(0x000E7F78)),
                struct.unpack("<i", p.read(0x000E7F30, 4))[0], struct.unpack("<i", p.read(0x000E7F34, 4))[0])
        lines.append(row)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
