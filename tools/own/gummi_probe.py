"""Read-only probe for the Gummi Ship tests: at each snapshot frame the game mode word (0x0032BA24: 2 = flight,
3 = Gummi Menu), and, while the flight module is loaded (0x636A at 0x01F18014), the score (0x01F8039C), the kills
(0x01F80856), the player ship (0x01F7DE44: hull +0x4AC, state +0x50C: 1 in, 2 control, 3 done, 4 destroyed)
and the ship's offset from its path (0x01F7DEE0: x, y).
  python -I tools/own/gummi_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        row = "f%d mode %d" % (fr, p.r32(0x0032BA24))
        if p.r16(0x01F18014) == 0x636A:
            ship = p.r32(0x01F7DE44)
            row += " | flight: score %d kills %d" % (p.r32(0x01F8039C), p.r16(0x01F80856))
            if 0x01000000 <= ship < 0x02000000:
                x, y = struct.unpack("<2f", p.read(0x01F7DEE0, 8))
                row += " | ship hull %.0f state %d offset (%.0f, %.0f)" % (p.rf(ship + 0x4AC), p.r32(ship + 0x50C), x, y)
            s1, s2, n2 = struct.unpack("<3I", p.read(0x000F2600, 12))      # the twenty-seventh glue's ships
            if 0x01000000 <= s2 < 0x02000000:
                x2, y2 = struct.unpack("<2f", p.read(0x000F2610, 8))
                row += " | ship 2 hull %.0f state %d offset (%.0f, %.0f) updates %d%s" % (
                    p.rf(s2 + 0x4AC), p.r32(s2 + 0x50C), x2, y2, n2, "" if s1 == ship else " (SHIP 1 IS NOT THE GAME'S)")
            else:
                row += " | no ship 2"
        elif p.r16(0x01F18014) == 0x62B0:
            row += " | Gummi Menu module"
        lines.append(row)
    except Exception as e:  # noqa: BLE001
        lines.append("f%d: read failed: %s" % (fr, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
