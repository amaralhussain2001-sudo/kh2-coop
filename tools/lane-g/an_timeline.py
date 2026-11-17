"""Lane G: print a timeline of chosen fields from a recorded run (one line whenever any of them changes).

  python -I tools/lane-g/an_timeline.py <test-name> <from-frame> <to-frame> <field> [<field> ...]
  field = block+OFF[:size][:f]     e.g.  obj1+154  twin+154  S+18  S+a30:4:f  slots+10d8
  size 1/2/4 (default 4); ":f" prints a float. Pads are always shown. Frames are session frames.
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load, buttons  # noqa: E402

CARG = None
if "--c" in sys.argv:
    i = sys.argv.index("--c")
    CARG = int(sys.argv[i + 1])
    del sys.argv[i:i + 2]
rec = load(sys.argv[1])
f0, f1 = int(sys.argv[2]), int(sys.argv[3])
fields = []
for spec in sys.argv[4:]:
    parts = spec.split(":")
    blk, off = parts[0].split("+")
    size = int(parts[1]) if len(parts) > 1 and parts[1] else 4
    fl = len(parts) > 2 and parts[2] == "f"
    fields.append((spec, blk, int(off, 16), size, fl))
S = rec.samples
first = next((s["vc"] for s in S if "O" in buttons(s["pad2"]).split("+")), None)
C = CARG if CARG is not None else (4700 - first if first else 152)
last = None
print("frame  pad1 / pad2 | " + " ".join(f[0] for f in fields))
for s in S:
    fr = s["vc"] + C
    if not f0 <= fr < f1:
        continue
    vals = []
    for spec, blk, off, size, fl in fields:
        b = s[blk]
        if fl:
            vals.append(f"{struct.unpack_from('<f', b, off)[0]:.1f}")
        else:
            v = int.from_bytes(b[off:off + size], "little")
            vals.append(f"{v:X}")
    row = (buttons(s["pad1"]), buttons(s["pad2"]), tuple(vals))
    if row != last:
        print(f"{fr:5d}  {row[0] or '-':>4} / {row[1] or '-':<4} | " + " ".join(vals))
        last = row
