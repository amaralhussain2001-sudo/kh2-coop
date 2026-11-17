"""Lane G: does a hero react to its controller exactly like the lone Sora of the reference run?

  python -I tools/lane-g/an_equiv.py <ref-test> <ref-start> <test> <block> <start> <length> [--c N] [--refc N] [--show]
Compares, frame by frame relative to <start>: position change since the start (x, y, z), and the action fields
object+0x154, +0x160, +0x2F8, +0xB04 (low 16 bits) and +0xB14. (+0xA0C is a serial number shared by all attackers, so it is not compared.)
<block> = obj1 or twin. The reference block is always obj1 of <ref-test>.
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load  # noqa: E402


def opt(name, default):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = int(sys.argv[i + 1])
        del sys.argv[i:i + 2]
        return v
    return default


NOY = "--noy" in sys.argv
if NOY:
    sys.argv.remove("--noy")
show = "--show" in sys.argv
if show:
    sys.argv.remove("--show")
C, RC = opt("--c", 152), opt("--refc", 152)
ref_name, ref_start, name, blk, start, length = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
ref, rec = load(ref_name), load(name)


def series(r, block, c, t0, n):
    out = {}
    base = None
    for s in r.samples:
        fr = s["vc"] + c - t0
        if fr < 0 or fr >= n or block not in s:
            continue
        b = s[block]
        x, y, z = struct.unpack_from("<3f", b, 0x70)
        a0c = struct.unpack_from("<I", b, 0xA0C)[0]
        if base is None:
            base = (x, y, z, a0c)
        st = (struct.unpack_from("<I", b, 0x154)[0], struct.unpack_from("<I", b, 0x160)[0], struct.unpack_from("<I", b, 0x2F8)[0],
              struct.unpack_from("<I", b, 0xB04)[0] & 0xFFFF, struct.unpack_from("<I", b, 0xB14)[0])
        out[fr] = (round(x - base[0], 1), round(y - base[1], 1), round(z - base[2], 1)) + st
    return out


A = series(ref, "obj1", RC, ref_start, length)
B = series(rec, blk, C, start, length)
common = sorted(set(A) & set(B))
bad = [f for f in common if A[f] != B[f]]
# tolerate tiny float differences in positions
real_bad = []
for f in bad:
    pa, pb = A[f], B[f]
    if pa[3:] != pb[3:] or any(abs(u - v) > 0.6 for u, v in zip((pa[0], pa[2]) + ((pa[1],) if not NOY else ()), (pb[0], pb[2]) + ((pb[1],) if not NOY else ()))):
        real_bad.append(f)
print(f"{name} {blk} from {start} vs {ref_name} from {ref_start}: {len(common)} common frames, {len(real_bad)} differ"
      + (f" (first at +{real_bad[0]})" if real_bad else "  => SAME BEHAVIOUR"))
if show or real_bad:
    lim = 14
    for f in (real_bad[:lim] if not show else common[:200:4]):
        print(f"   +{f:4d} ref {A[f]}  got {B[f]}")
