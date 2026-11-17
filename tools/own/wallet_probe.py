"""Read-only probe (ninth round, the sixty-ninth glue: player 2's own wallet). At each snapshot frame: the game mode word,
player 1's wallet (save + 0x2440 = 0x0032DF70), player 2's wallet (King Mickey's record + 0x48 = 0x0032E3A4) and its mark
(+ 0x4C), whose shop (0x000E7FA8), "player 2's menu things are in" (0x000E7E24), who ran the last green command
(0x000E7FA0: P1 / P2) and when (0x000E7FA4), the bag's seven fight items (save + 0x3580) and player 2's stock of them
(King Mickey's record + 0x24), the bag's first armours and accessories.
  python -I tools/own/wallet_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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

for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        cmd = p.r32(0x000E7FA0)
        who = "P1" if cmd == h1 and cmd else "P2" if cmd == h2 and cmd else "%08X" % cmd
        bag = p.read(0x0032F0B0, 8)
        st2 = p.read(0x0032E380, 8)
        lines.append("f%d mode %d | wallet P1 %d P2 %d mark %04X | shop %d menu2 %d | last command %s at %d (counter %d) | bag 0-6 %s | P2 stock %s" % (
            fr, p.r32(0x0032BA24), p.r32(0x0032DF70), p.r32(0x0032E3A4), p.r16(0x0032E3A8), p.r32(0x000E7FA8),
            p.r32(0x000E7E24), who, p.r32(0x000E7FA4), p.r32(0x0034D4BC), bag[0:7].hex(" "), st2[:7].hex(" "))
            + " | heroes %08X %08X" % (h1, h2))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
