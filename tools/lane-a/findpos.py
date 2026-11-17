"""Lane A: find float position triples (x, ?, z) in a RAM dump.

  python -I tools/lane-a/findpos.py <ram.bin> <x> <z> [tolerance]
Prints addresses where a float within tolerance of x is followed 8 bytes later by a float within tolerance of z.
"""
import struct
import sys

ram = open(sys.argv[1], "rb").read()
x, z = float(sys.argv[2]), float(sys.argv[3])
tol = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
n = len(ram) // 4
f = struct.unpack(f"<{n}f", ram[:n * 4])
hits = []
for i in range(n - 2):
    v = f[i]
    if v == v and abs(v - x) <= tol and abs(f[i + 2] - z) <= tol:
        hits.append(i * 4)
for h in hits:
    print(f"0x{h:08X}  x={f[h // 4]:.2f} y={f[h // 4 + 1]:.2f} z={f[h // 4 + 2]:.2f} w={f[h // 4 + 3]:.2f}")
print("hits:", len(hits))
