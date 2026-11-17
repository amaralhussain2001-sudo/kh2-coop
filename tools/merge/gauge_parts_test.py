"""ONE-COPY TEST ONLY (memory writes): find out which parts of player 2's small gauge are the rings.

  python -I tools/merge/gauge_parts_test.py <testDir> <pinePort> <firstFrame> <step> <out.txt>

The harness must take screenshots at firstFrame, firstFrame + step, ... (one per part + 1).
After screenshot k the probe hides part k (flag 0x40 in the part's flag word) and shows part k - 1 again, so
screenshot k + 1 shows the gauge without part k. Parts = the 2D objects embedded in the gauge object
(lane V2's twin gauge, pointer at 0x000F7F00), found by their class words.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

test_dir, port, first, step, out = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
CLASSES = {0x0034A958: "sequence", 0x00348658: "bar", 0x0034A800: "root", 0x00348678: "bar2", 0x00347E60: "seq2"}
p = Pine(port, wait=120)
log = []


def wait_snap(fr, limit=600):
    f = test_dir / ("p1_f%06d.png" % fr)
    t0 = time.time()
    while not f.exists() and time.time() - t0 < limit:
        time.sleep(0.02)
    return f.exists()


if not wait_snap(first):
    sys.exit("first screenshot never appeared")
g = p.r32(0x000F7F00)
raw = p.read(g, 0x15B0)
parts = []
for off in range(0x20, 0x15B0, 4):
    w = struct.unpack_from("<I", raw, off)[0]
    if w in CLASSES:
        flags, group = struct.unpack_from("<II", raw, off + 12)
        if group == 0x30:
            parts.append((off, CLASSES[w], flags))
log.append("twin gauge at %08X; parts (offset, kind, flags): %s" % (g, ", ".join("+%X %s %X" % x for x in parts)))
fr = first
prev = None
for off, kind, flags in parts:
    if prev is not None:
        p.w32(g + prev[0] + 12, prev[2])                 # show the previous part again (its old flags)
    p.w32(g + off + 12, flags | 0x40)
    fr += step
    log.append("screenshot f%06d: part +%X (%s) hidden" % (fr, off, kind))
    prev = (off, kind, flags)
    if not wait_snap(fr):
        log.append("screenshot %d never appeared" % fr)
        break
if prev is not None:
    p.w32(g + prev[0] + 12, prev[2])
open(out, "w", encoding="utf-8").write("\n".join(log) + "\n")
print("\n".join(log))
