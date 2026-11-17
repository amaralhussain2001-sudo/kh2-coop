"""Read-only probe: at every snapshot frame print memory ranges as hex words (one line per 16 bytes).

  RANGES=0032BAD0:60,0032BB30:20 python -I tools/own/memdump_probe.py <testDir> <pinePort> <frame,...> <out.txt>

RANGES = start:length pairs (hex). Default: the game's four place records (now, next, back-to, last) and the
start of the save data.
CHAINS = pointer chains, for example 01D49320+8:40 = read the word at 01D49320, add 8, read the word there,
print 0x40 bytes from it; 01D49320:40 = print 0x40 bytes of the object the word points to.
"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
ranges = [tuple(int(v, 16) for v in r.split(":")) for r in os.environ.get("RANGES", "0032BAD0:60,0032BB30:20").split(",")]
chains = [c for c in os.environ.get("CHAINS", "").split(",") if c]
p = Pine(port, wait=120)
t0 = time.time()
lines = []
seen = 0
while seen < len(frames) and time.time() - t0 < 900.0:
    f = frames[seen]
    if not (test_dir / ("p1_f%06d.png" % f)).exists():
        time.sleep(0.02)
        continue
    seen += 1
    for a, n in ranges:
        try:
            data = p.read(a, n)
            for k in range(0, n, 16):
                lines.append("f%d %08X  %s" % (f, a + k, " ".join("%02X" % b for b in data[k:k + 16])))
        except Exception as e:  # noqa: BLE001
            lines.append("f%d %08X read failed: %r" % (f, a, e))
    for c in chains:
        try:
            path, n = c.split(":")
            path, _, skip = path.partition("@")  # 0034E948+48C@1A0:20 = 0x20 bytes from offset 0x1A0 of the object
            steps = path.split("+")
            a = p.r32(int(steps[0], 16))
            for s in steps[1:]:
                a = p.r32(a + int(s, 16)) if 0x00100000 <= a < 0x02000000 else 0
            if not 0x00100000 <= a < 0x02000000:
                lines.append("f%d chain %s -> %08X (no object)" % (f, c, a))
                continue
            a += int(skip, 16) if skip else 0
            data = p.read(a, int(n, 16))
            for k in range(0, len(data), 16):
                lines.append("f%d chain %s %08X  %s" % (f, path, a + k, " ".join("%02X" % b for b in data[k:k + 16])))
        except Exception as e:  # noqa: BLE001
            lines.append("f%d chain %s read failed: %r" % (f, c, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
