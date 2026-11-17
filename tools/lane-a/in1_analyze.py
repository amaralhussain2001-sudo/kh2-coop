"""Lane A: show how the controller region changes per held input (test a-in1).

  python -I tools/lane-a/in1_analyze.py <test-out-dir> <rangeStartHex> [stride]
Prints every byte offset in the range whose value differs from the idle window in at least one window.
"""
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
start = int(sys.argv[2], 16)
frames = [6500, 6750, 7350, 7950, 8550, 9150, 9750, 10350, 10950, 11550, 12150, 12750, 13350, 13950, 14550, 15150, 15750]
names = ["idle", "1LX+", "1LY-", "1X", "1O", "1SQ", "1TRI", "1L1", "1R1", "2LX+", "2LY-", "2X", "2O", "2SQ", "2TRI", "2L1", "2R1"]
M = [(d / f"mem_f{f:06d}_{start:08X}.bin").read_bytes() for f in frames]
n = len(M[0])
print("addr      " + " ".join(f"{x:>5s}" for x in names))
for o in range(0, n, 4):
    words = [int.from_bytes(m[o:o + 4], "little") for m in M]
    if len(set(words)) == 1:
        continue
    base = words[0]
    cells = []
    for w in words:
        cells.append("    ." if w == base and w is not words[0] else f"{w:08X}"[-8:])
    print(f"{start + o:08X}  " + " ".join(f"{w:08X}" if (i == 0 or w != base) else "       ." for i, w in enumerate(words)))
