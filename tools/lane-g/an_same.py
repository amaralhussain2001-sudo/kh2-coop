"""Lane G: are two recorded runs byte-identical in the recorded blocks (same frames)?  Used for "one player alone,
patch on" against "one player alone, no patch".

  python -I tools/lane-g/an_same.py <testA> <testB> [block ...]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load  # noqa: E402

a, b = load(sys.argv[1]), load(sys.argv[2])
blocks = sys.argv[3:] or [k for k in a.samples[0] if k != "vc" and k in b.samples[0]]
A = {s["vc"]: s for s in a.samples}
B = {s["vc"]: s for s in b.samples}
common = sorted(set(A) & set(B))
print(f"{sys.argv[1]} vs {sys.argv[2]}: {len(common)} common frames (pad counter {common[0]}..{common[-1]})")
for blk in blocks:
    bad = [vc for vc in common if A[vc][blk] != B[vc][blk]]
    msg = "IDENTICAL" if not bad else f"{len(bad)} frames differ, first at pad counter {bad[0]}"
    if bad:
        x, y = A[bad[0]][blk], B[bad[0]][blk]
        offs = [i for i in range(len(x)) if x[i] != y[i]]
        msg += f" (bytes +0x{offs[0]:X}..+0x{offs[-1]:X}, {len(offs)} bytes)"
    print(f"  {blk:6s} {msg}")
if "S2" in blocks:
    nz = [vc for vc in sorted(B) if any(B[vc]["S2"])]
    print("  S2 area in", sys.argv[2], "all zero in every sample" if not nz else f"NOT zero from pad counter {nz[0]}")
