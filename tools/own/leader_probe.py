"""Read-only probe: where does memory hold the pointer to player 1's hero (and to the twin)? At each snapshot
frame the program's data (0x00300000-0x00A00000), the cave (0x000F0000-0x000F8000) and the object heap
(0x01A00000-0x01D80000) are read and searched for the two pointer values. Hits inside the helpers' own objects
are marked. One line per hit.

  python -I tools/own/leader_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []
RANGES = ((0x000F0000, 0x000F8000), (0x00300000, 0x00A00000), (0x01A00000, 0x01D80000))

for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        party = struct.unpack("<3I", p.read(0x00348638, 12))
        lines.append("frame %d | player %08X twin %08X | party %08X %08X %08X" % ((fr, pl, tw) + party))
        objs = [("player", pl), ("twin", tw), ("helper1", party[1]), ("helper2", party[2])]
        for a, b in RANGES:
            blob = p.read(a, b - a)
            words = struct.unpack("<%dI" % (len(blob) // 4), blob)
            for i, w in enumerate(words):
                if w and w in (pl, tw):
                    addr = a + 4 * i
                    where = ""
                    for name, o in objs:
                        if o and o <= addr < o + 0x1400:
                            where = " (%s + 0x%X)" % (name, addr - o)
                    lines.append("  %08X = %s%s" % (addr, "PLAYER" if w == pl else "TWIN", where))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
