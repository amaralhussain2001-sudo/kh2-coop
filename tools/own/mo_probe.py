"""Read-only probe (part 141, the seventy-ninth glue --menuowner). Polls all the time and writes every CHANGE of: the screen's owner
(V_OWNER 0x000DE800), when it was set (V_OWNSTEP 0x000DE804), who ran the last green command (0x000E7FA0: P1 / P2) and player 2's
menu flag (0x000E7E24) and the game's "no pause menu now" word (0x0034D840) and when a message window last asked (0x000DE808), each with the game's counter (0x0034D4BC); and one line at each snapshot frame.
  python -I tools/own/mo_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))
last = None
i = 0


def state():
    h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
    cmd = p.r32(0x000E7FA0)
    who = "P1" if cmd == h1 and cmd else "P2" if cmd == h2 and cmd else ("-" if not cmd else "%08X" % cmd)
    return (p.r32(0x000DE800), p.r32(0x000DE804), who, p.r32(0x000E7FA4), p.r32(0x000E7E24), p.r32(0x0034D840), p.r32(0x000DE808), p.r32(0x000DE80C)), p.r32(0x0034D4BC)


while i < len(frames) and time.time() - t0 < WAIT:
    try:
        s, ctr = state()
        if s != last:
            lines.append("counter %d: owner %d (set at %d) | last command %s at %d | menu2 %d | no-menu word %08X | box asked at %d | other caller %08X" % (ctr, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]))
            last = s
        snap = test_dir / ("p1_f%06d.png" % frames[i])
        if snap.exists():
            lines.append("f%d (counter %d): owner %d" % (frames[i], ctr, s[0]))
            i += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("read failed: %s" % ex)
        time.sleep(0.5)
    time.sleep(0.01)
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
