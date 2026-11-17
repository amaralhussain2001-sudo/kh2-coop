"""Read-only probe (tenth round, the move of glue 66's shots' table to 0x000DF000): at each snapshot frame, while the
Gummi flight module is loaded, the score split (as gscore_probe.py) AND the shots' table: how many bytes of
0x000DF000 .. 0x000DFFFF hold 1 (ship 1), 2 (ship 2), other non-zero (= another writer: must be 0); the non-zero bytes
of 0x000D0000 .. 0x000DEFFF (the memory below it: must be 0); and the patch words of 0x000EE800 .. 0x000EEF7F that read
different from the patch (glues 72 .. 75's code, where the old table lay; must be 0).
  python -I tools/own/gqtab_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
PATCH = pathlib.Path(__file__).resolve().parents[2] / "patches" / "test-own-v137" / "SLPM-66675_F266B00B.pnach"
code = {}
for line in open(PATCH, encoding="utf-8"):
    m = re.match(r"patch=\d+,EE,([0-9A-Fa-f]{8}),word,([0-9A-Fa-f]{8})", line.strip())
    if m and 0x000EE800 <= int(m.group(1), 16) < 0x000EF800:
        code[int(m.group(1), 16)] = int(m.group(2), 16)
p = Pine(port, wait=120)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "900"))
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    try:
        row = "f%d mode %d" % (fr, p.r32(0x0032BA24))
        if p.r16(0x01F18014) == 0x636A:
            score, p2 = p.r32(0x01F8039C), p.r32(0x000E7EFC)
            row += " | score %d = player 1's %d + player 2's %d | kills %d" % (score, score - p2, p2, p.r16(0x01F80856))
        tab = p.read(0x000DF000, 0x1000)
        below = p.read(0x000D0000, 0xF000)
        bad = sum(1 for a, w in code.items() if p.r32(a) != w)
        row += " | table: ship1 %d ship2 %d other %d | below non-zero %d | old-table code words changed %d of %d" % (
            tab.count(1), tab.count(2), sum(1 for b in tab if b not in (0, 1, 2)), sum(1 for b in below if b), bad, len(code))
        lines.append(row)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
