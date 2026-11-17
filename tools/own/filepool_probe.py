"""Read-only probe: THE GAME'S OBJECT FILE POOL at each snapshot frame (eighth round, plan row 44 / fault F6).
The loader keeps one list of file entries (head 0x0034DCA0, next at + 0x3C), sorted by their keep-number (+ 0x28):
low numbers first. Each entry has a size (+ 0x2C) and a place (+ 0x30) in the pool; the pool's limit is the word
0x0034DCB0. Entries that do not fit below the limit are unloaded (0x001700E8), whatever still uses them.
  python -I tools/own/filepool_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
One block per frame: the limit, the number of entries, the sum of sizes, and every entry with a keep-number of
2000 or more (number, size, place, state bytes, the text found in the entry). LOW=<n> changes the 2000."""
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
LOW = int(os.environ.get("LOW", "2000"))
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def text_of(raw):
    best = b""
    cur = b""
    for b in raw:
        if 0x20 <= b < 0x7F:
            cur += bytes([b])
        else:
            if len(cur) > len(best):
                best = cur
            cur = b""
    if len(cur) > len(best):
        best = cur
    return best.decode("ascii", "replace") if len(best) >= 4 else ""


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        head = p.r32(0x0034DCA0)
        limit = p.r32(0x0034DCB0)
        ents, a, n = [], head, 0
        while 0x00100000 <= a < 0x02000000 and n < 600:
            raw = p.read(a, 0x40)
            w = struct.unpack("<16I", raw)
            ents.append((a, w[10], w[11], w[12], raw[0], raw[1], w[14], text_of(raw[2:0x24])))
            a = w[15]
            n += 1
        total = sum(e[2] for e in ents)
        lines.append("f%d: limit %08X (%d), %d entries, sizes %d bytes, last place+size %d; abort recorder count %d" % (
            fr, limit, limit, len(ents), total, max([e[3] + e[2] for e in ents] or [0]), p.r32(0x000E7100)))
        for e in ents:
            if e[1] >= LOW:
                lines.append("   %08X number %5d size %7d place %8d state %d %d was %5d  %s" % e)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d readfail %s" % (fr, ex))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
