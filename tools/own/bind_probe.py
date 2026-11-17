"""Read-only probe (ninth round, register F8): HOW EACH HERO'S BODY AND WEAPONS ARE BOUND TO THEIR FILES. At each
snapshot frame, for player 1's hero, the twin and their weapons (first / second hand): the object, its object
number and model name, and the binding record at object + 0x7A0 (the files' number, the model file's place, the
effect file's place, the motion file's place: a place of 0 = not bound). Then the file pool's entries with the
numbers 2300 .. 2399 and 5000 .. 5099 (number, name, size, place, where the data is now, state).
  python -I tools/own/bind_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def ok(a):
    return 0x00080000 <= a < 0x02000000


def text_of(raw):
    best, cur = b"", b""
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


def bound(o):
    if not ok(o):
        return "none"
    e = p.r32(o + 8)
    name = "%04X %s" % (p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20))) if ok(e) else "no entry"
    num, objn, ent, mdl, afm, mset = struct.unpack("<6I", p.read(o + 0x7A0, 24))
    return "%08X %s number %d model %08X effect %08X motion %08X" % (o, name, num, mdl, afm, mset)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x0034E948), p.r32(0x000F05CC)
        lines.append("f%d" % fr)
        for who, h in (("P1", h1), ("P2", h2)):
            lines.append("   %s body   %s" % (who, bound(h)))
            if ok(h):
                for hand in (0, 1):
                    w = p.r32(h + 0xAF8 + 4 * hand)
                    if ok(w):
                        lines.append("   %s hand %d %s" % (who, hand, bound(w)))
        a, n = p.r32(0x0034DCA0), 0
        while ok(a) and n < 600:
            raw = p.read(a, 0x40)
            w = struct.unpack("<16I", raw)
            if 2300 <= w[10] < 2400 or 5000 <= w[10] < 5100:
                lines.append("      pool %d %-28s size %7d place %08X data at %08X state %d kind %d" % (
                    w[10], text_of(raw[2:0x24]).replace("obj/", ""), w[11], w[12], w[13], raw[1], raw[0]))
            a = w[15]
            n += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
