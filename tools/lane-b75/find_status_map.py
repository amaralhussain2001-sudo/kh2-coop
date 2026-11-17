"""Look for the table that turns an object's status number (category*1000 + index) into an enemy-table id.

Known pairs for category 5 (from the community list, to be verified): index 1 -> 19, 2 -> 18, 6 -> 20, 9 -> 138,
12 -> 71, 46 -> 128. Searches files for an array (element size 1, 2 or 4 bytes) that satisfies them.

  python -I tools/lane-b75/find_status_map.py <file> [<file> ...]
"""
import struct
import sys

PAIRS = {1: 19, 2: 18, 6: 20, 9: 138, 12: 71, 46: 128}
FMT = {1: "<B", 2: "<H", 4: "<I"}

for path in sys.argv[1:]:
    data = open(path, "rb").read()
    found = 0
    for size in (1, 2, 4):
        key = struct.pack(FMT[size], PAIRS[1]) + struct.pack(FMT[size], PAIRS[2])
        pos = data.find(key)
        while pos != -1:
            base = pos - size  # element 0
            ok = base >= 0
            if ok:
                for idx, val in PAIRS.items():
                    o = base + idx * size
                    if o + size > len(data) or struct.unpack_from(FMT[size], data, o)[0] != val:
                        ok = False
                        break
            if ok:
                found += 1
                vals = [struct.unpack_from(FMT[size], data, base + i * size)[0] for i in range(72)]
                print("%s: element size %d, table starts at file offset 0x%X" % (path.replace("\\", "/").rsplit("/", 1)[-1], size, base))
                print("   first 72 values:", vals)
            pos = data.find(key, pos + 1)
    if not found:
        print("%s: no such table" % path.replace("\\", "/").rsplit("/", 1)[-1])
