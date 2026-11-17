"""Read-only probe for the heap recorder kit (tools/own/make_heapkit.py): sweep_probe.py's line for each snapshot
frame, plus the object heap's state from the kit's value block 0x000F1F80.
  python -I tools/own/heap_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
One line per frame:
  f<frame> room .. P1 .. P2 .. msn . go . | heap <size> use <now> free <now> big <largest piece now> blk <blocks>
  and one last line "WORST": most in use, smallest free sum, smallest largest piece (with the session frame),
  most blocks, failed allocations (size, caller), the biggest request (size, caller). Sizes in bytes."""
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
V = 0x000F1F80
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "200"))


def hero(o):
    if not 0x00100000 <= o < 0x02000000:
        return "none"
    s = p.r32(o + 0x48C)
    if not 0x00100000 <= s < 0x02000000:
        return "noslot"
    return "%d/%d a%02X" % (p.r32(s), p.r32(s + 4), p.r32(o + 0x154) & 0xFFFF)


def block():
    return struct.unpack("<16I", p.read(V, 64))


last = None
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        v = block()
        last = v
        lines.append("f%d room %04X btl %d L%d P1 %s P2 %s msn %d go %d | heap %d use %d free %d big %d blk %d" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r8(0x000F6F00), hero(p.r32(0x0034E948)),
            hero(p.r32(0x000F05CC)), 1 if p.r32(0x01D49320) else 0, 1 if p.r32(0x00350DF0) else 0,
            v[14], v[8], v[11], v[9], v[10]))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail" % fr)
try:
    last = block()
except Exception:  # noqa: BLE001
    pass
if last:
    v = last
    lines.append("WORST heap %d at %08X: most in use %d, smallest free sum %d, smallest largest piece %d (frame %d), "
                 "most blocks %d, failed %d (size %d, caller %08X), biggest request %d (caller %08X)" % (
                     v[14], v[15], v[0], 0x7FFFFFFF - v[13], 0x7FFFFFFF - v[1], v[2] + 152, v[12], v[3], v[4], v[5],
                     v[6], v[7]))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
