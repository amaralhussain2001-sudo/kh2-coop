"""Read-only probe for tools/own/make_abortrec.py: waits until the recorder has caught abort() / exit() (the game
spins there, so its memory can still be read), then writes: the recorder's words, the code addresses on the
saved stack, WHAT EVERY OBJECT ON THAT STACK IS (class table, object id and model name from its object entry, its
motion part's resource and that resource's class table), the heroes' pointers and the party table.
  python -I tools/own/abort_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
If nothing is caught by the last snapshot frame it says so."""
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
p = Pine(port, wait=120)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "400"))
last = test_dir / ("p1_f%06d.png" % frames[-1])
R = 0x000E7100
n = 0
while time.time() - t0 < WAIT:
    try:
        n = p.r32(R)
    except Exception:  # noqa: BLE001
        time.sleep(0.2)
        continue
    if n or last.exists():
        break
    time.sleep(0.05)


def is_obj(a):
    return 0x01800000 <= a < 0x02000000 and a % 4 == 0


def is_data(a):
    return 0x00330000 <= a < 0x00380000


def name_of(o):
    try:
        cls = p.r32(o)
        if not is_data(cls):
            return "class %08X (not a class table: not an object, or a dead one)" % cls
        e = p.r32(o + 8)
        s = "class %08X" % cls
        if 0x00100000 <= e < 0x02000000:
            raw = p.read(e, 0x30)
            oid = struct.unpack_from("<I", raw, 0)[0]
            nm = raw[8:40].split(b"\0")[0].decode("ascii", "replace")
            s += " entry %08X id %04X model %s" % (e, oid & 0xFFFF, nm)
        res = p.r32(o + 0x140 + 12)
        s += " | motion resource %08X" % res
        if 0x00100000 <= res < 0x02000000:
            rc = p.r32(res)
            s += " class %08X%s" % (rc, "" if is_data(rc) else " <- DEAD")
        return s
    except Exception as ex:  # noqa: BLE001
        return "unreadable (%s)" % ex


if not n:
    lines.append("nothing caught: abort() / exit() was not called")
else:
    head = struct.unpack("<8I", p.read(R, 32))
    lines.append("CAUGHT %d call(s): return address %08X, sp %08X, a0 %08X, game counter %d (session frame about %d)" % (
        head[0], head[1], head[2], head[3], head[4], head[4] + 152))
    st = struct.unpack("<256I", p.read(R + 0x20, 0x400))
    seen = []
    for i in range(0, 256, 2):
        v = st[i]
        if 0x00100000 <= v < 0x00340000:
            lines.append("   sp+%03X %08X <- code" % (i * 4, v))
        elif is_obj(v):
            lines.append("   sp+%03X %08X" % (i * 4, v))
            if v not in seen:
                seen.append(v)
    lines.append("OBJECTS ON THE STACK:")
    for v in seen:
        lines.append("   %08X: %s" % (v, name_of(v)))
        if v >= 0x140 and is_obj(v - 0x140):
            lines.append("   %08X (= that - 0x140): %s" % (v - 0x140, name_of(v - 0x140)))
    lines.append("WHO IS WHO:")
    for label, a in (("player 1's hero (00352400)", 0x00352400), ("engine's player (0034E948)", 0x0034E948),
                     ("parking place (0034E94C)", 0x0034E94C), ("the twin (000F05CC)", 0x000F05CC),
                     ("party place 1 (0034863C)", 0x0034863C), ("party place 2 (00348640)", 0x00348640)):
        o = p.r32(a)
        lines.append("   %s = %08X %s" % (label, o, name_of(o) if is_obj(o) else ""))
    for label, a in (("player 1's hero", 0x00352400), ("the twin", 0x000F05CC)):
        o = p.r32(a)
        if is_obj(o):
            for off in (0xAC8, 0xACC, 0xAF8, 0xAFC, 0xB00, 0xB40):
                w = p.r32(o + off)
                lines.append("   %s + %03X = %08X %s" % (label, off, w, name_of(w) if is_obj(w) else ""))
    rec = p.r32(0x00351184)
    if 0x00100000 <= rec < 0x02000000:
        r = struct.unpack("<8I", p.read(rec, 32))
        lines.append("   form record: body %08X form %d object id %04X flags %08X handle %08X slot %08X task %08X" % (
            r[0], r[1], r[2] & 0xFFFF, r[3], r[4], r[5], r[6]))
    lines.append("   forms: player 1's %d, the twin's %d; lock words %08X %08X; form record %08X" % (
        p.r8(0x0032F054), p.r8(0x000F47E8), p.r32(0x00351EB8), p.r32(0x00351EC0), p.r32(0x00351184)))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
