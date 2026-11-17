"""List the free gaps of a patch folder between two addresses (words that the patch does not write).
  python -I tools/own/patch_gaps.py <patchDir> <fromHex> <toHex> [minWords]"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
f = ROOT / sys.argv[1] / "SLPM-66675_F266B00B.pnach"
a, b = int(sys.argv[2], 16), int(sys.argv[3], 16)
least = int(sys.argv[4]) if len(sys.argv) > 4 else 16
used = set()
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"patch=1,EE,([0-9A-Fa-f]{8}),(\w+),", line)
    if m:
        ad = int(m.group(1), 16) & 0x0FFFFFFF
        used.add(ad & ~3)
start = None
for ad in range(a, b + 4, 4):
    free = ad not in used and ad < b
    if free and start is None:
        start = ad
    if not free and start is not None:
        if (ad - start) // 4 >= least:
            print("%08X .. %08X  %d words free" % (start, ad, (ad - start) // 4))
        start = None
