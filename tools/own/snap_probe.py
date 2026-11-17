"""Read-only probe (ninth round, the own wallet and bag): THE GAME'S CONTINUE SNAPSHOT (the whole save data copied to 0x01D499B0
at a room load, part 1 of the sixth round) against the live save data: both wallets, King Mickey's record + 0x14 .. + 0x53
(player 2's item places, stock, shortcuts, switches, Keyblade, wallet, marks), player 2's bag (King Mickey's ability places
16 .. 79), the game's bag (save + 0x3580 .. + 0x36B7) and the hero's armour / accessory places (Sora's record + 0x14 ..
+ 0x33); "same" or the first differing offsets. Also the swap flags (0x000E7E24, 0x000E7FAC) and whose shop (0x000E7FA8).
  python -I tools/own/snap_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
SAVE, SNAP = 0x0032BB30, 0x01D499B0
PARTS = (("wallet P1", 0x2440, 4), ("Mickey 14-53", 0x2840, 0x40), ("P2 bag", 0x28A0, 0x80), ("game's bag", 0x3580, 0x138),
         ("Sora's places", 0x2504, 0x20))

for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        row = "f%d menu2 %d bag in %d shop %d | wallets live %d / %d, snapshot %d / %d" % (
            fr, p.r32(0x000E7E24), p.r32(0x000E7FAC), p.r32(0x000E7FA8), p.r32(SAVE + 0x2440), p.r32(SAVE + 0x2874),
            p.r32(SNAP + 0x2440), p.r32(SNAP + 0x2874))
        for name, off, n in PARTS:
            a, b = p.read(SAVE + off, n), p.read(SNAP + off, n)
            diff = [k for k in range(n) if a[k] != b[k]]
            row += " | %s: %s" % (name, "same" if not diff else "differ at +%s" % ",".join("%X" % (off + k) for k in diff[:6]))
        lines.append(row)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
