"""TEST ONLY (part 142: different picture quality on the two PCs). Compares the two copies' EE main memory dumps of a run
(p1_ram_fNNNNNN.bin / p2_ram_fNNNNNN.bin, written by the session key DumpFrames at the SAME session frame) and prints, per frame,
how many bytes differ and in which address ranges (runs closer than 256 bytes are joined). Deletes the dumps unless --keep.
  python -I tools/own/ramdiff.py <testDir> [--keep]
"""
import pathlib
import re
import sys

d = pathlib.Path(sys.argv[1])
keep = "--keep" in sys.argv
PAGE = 4096
KNOWN = (0x00457580, 0x004F3580)  # the picture copy area of the field (lane V3; part 142)
frames = sorted({int(m.group(1)) for p in d.glob("p1_ram_f*.bin") for m in [re.search(r"f(\d+)\.bin$", p.name)] if m})
out = []
for f in frames:
    a_p, b_p = d / ("p1_ram_f%06d.bin" % f), d / ("p2_ram_f%06d.bin" % f)
    if not b_p.exists():
        out.append("f%d: no p2 dump" % f)
        continue
    a, b = a_p.read_bytes(), b_p.read_bytes()
    if len(a) != len(b):
        out.append("f%d: sizes differ %d %d" % (f, len(a), len(b)))
        continue
    runs = []
    total = 0
    for off in range(0, len(a), PAGE):
        if a[off:off + PAGE] == b[off:off + PAGE]:
            continue
        for i in range(off, min(off + PAGE, len(a))):
            if a[i] != b[i]:
                total += 1
                if runs and i - runs[-1][1] <= 256:
                    runs[-1][1] = i
                else:
                    runs.append([i, i])
    if not runs:
        out.append("f%d: identical" % f)
    else:
        known = [r for r in runs if KNOWN[0] <= r[0] and r[1] < KNOWN[1]]
        other = [r for r in runs if not (KNOWN[0] <= r[0] and r[1] < KNOWN[1])]
        out.append("f%d: %d bytes differ in %d ranges, span %08X-%08X; inside %08X-%08X: %d ranges; OUTSIDE IT: %d ranges %s" % (
            f, total, len(runs), runs[0][0], runs[-1][1] + 1, KNOWN[0], KNOWN[1], len(known), len(other),
            " ".join("%08X-%08X" % (r[0], r[1] + 1) for r in other[:60]) + (" ..." if len(other) > 60 else "")))
    if not keep:
        a_p.unlink()
        b_p.unlink()
print("\n".join(out) if out else "no dumps")
