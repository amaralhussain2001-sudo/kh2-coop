"""Move one spawn entity inside a room file (.ard) in place: same size, only the three position floats change.

  python -I tools/lane-b/move_entity.py <file.ard> <objIdHex> <oldX> <oldZ> <newX> <newY> <newZ> [--all]
The entity is found by its object id followed by a position whose x and z are within 0.2 of oldX / oldZ.
Exactly one match is required unless --all is given.
"""
import struct
import sys

path = sys.argv[1]
oid = int(sys.argv[2], 16)
ox, oz, nx, ny, nz = (float(v) for v in sys.argv[3:8])
data = bytearray(open(path, "rb").read())
hits = []
for i in range(0, len(data) - 16, 4):
    if struct.unpack_from("<I", data, i)[0] != oid:
        continue
    x, y, z = struct.unpack_from("<3f", data, i + 4)
    if abs(x - ox) < 0.2 and abs(z - oz) < 0.2:
        hits.append(i)
if not hits or (len(hits) > 1 and "--all" not in sys.argv):
    sys.exit(f"expected one entity, found {len(hits)}")
for i in hits:
    struct.pack_into("<3f", data, i + 4, nx, ny, nz)
open(path, "wb").write(data)
print(f"moved {len(hits)} entity(ies) of object 0x{oid:X} to ({nx}, {ny}, {nz})")
