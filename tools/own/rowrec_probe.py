"""Read-only probe for the command-row recorder (tools/own/make_rowrec.py). At each snapshot frame, for each hero:
the commands judged so far (id: newest result, calls, calls not lit) and the state at the newest judged call.
  python -I tools/own/rowrec_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
Result 0 = lit, 5 = dim. Command ids: 1 Attack, 2 Magic, 3 Items, 4 Drive, 5 Revert, 6 Valor, 7 Wisdom,
11 Master, 12 Final, 72 Summon, 73 Party, 81 Limit (the game's command table)."""
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
        for who in (0, 1):
            ent = struct.unpack("<56I", p.read(0x000F1E00 + who * 0xE0, 224))
            st = struct.unpack("<8I", p.read(0x000F1FC0 + who * 0x20, 32))
            rows = ", ".join("%d: %d (%d calls, %d not lit)" % (ent[i], ent[i + 1], ent[i + 2], ent[i + 3])
                             for i in range(0, 56, 4) if ent[i + 2])
            lines.append("f%d P%d rows %s" % (fr, who + 1, rows or "-"))
            lines.append("f%d P%d state: 34F240 %08X, body form %d, control dim mask %08X, locks %08X / %08X, hero+588 %08X, "
                         "save form %d, at f%d" % (fr, who + 1, st[0], st[1], st[2], st[3], st[4], st[5], st[6], st[7] + 152))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail %r" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
