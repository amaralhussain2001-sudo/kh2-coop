"""Read-only probe (part 143, the eightieth glue --difficulty). At each snapshot frame: the difficulty word (0x000DE810), the twin
pointer, and every filled unit slot (slot k at 0x01C6C750 - 0x268 x (k - 1), k = 1 .. 48; + 0x264 = its enemy-table entry,
whose u16 at + 0 is the entry id; + 4 = the maximum of HP value 0) as "id:max", sorted, plus whether the id is a boss entry.
  python -I tools/own/hp_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import csv
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BOSS = {int(r["entry_id"]) for r in csv.DictReader(open(ROOT / "tools" / "lane-b75" / "data" / "boss_entries.csv", encoding="utf-8"))}
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
        units = []
        for k in range(1, 49):
            slot = 0x01C6C750 - 0x268 * (k - 1)
            ent = p.r32(slot + 0x264)
            if not (0x00100000 <= ent < 0x02000000):
                continue
            eid = p.r16(ent)
            units.append((eid, p.r32(slot + 4), k))
        units.sort()
        lines.append("f%d diff %d twin %08X | %s" % (fr, p.r32(0x000DE810), p.r32(0x000F05CC),
                     " ".join("%d%s:%d" % (e, "B" if e in BOSS else "", m) for e, m, _k in units)))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
