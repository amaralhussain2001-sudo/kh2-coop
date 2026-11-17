"""Count in how many rooms each object id is placed by the room spawn data (lane C's full room dumps).

  python -I tools/lane-b75/placements.py <laneC_ard_dir> <out.json>
Line format in the dumps: '    ENT obj 0x0236 pos ...'.
"""
import collections
import json
import os
import re
import sys

d = sys.argv[1]
pat = re.compile(r"ENT obj 0x([0-9A-Fa-f]+) ")
rooms = collections.defaultdict(set)
count = collections.Counter()
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".txt"):
        continue
    room = fn[:-4]
    for line in open(os.path.join(d, fn), encoding="utf-8", errors="replace"):
        m = pat.search(line)
        if m:
            o = int(m.group(1), 16)
            rooms[o].add(room)
            count[o] += 1
json.dump({"0x%X" % o: {"rooms": sorted(r), "placements": count[o]} for o, r in rooms.items()},
          open(sys.argv[2], "w", encoding="utf-8"), indent=0)
print("object ids placed somewhere:", len(rooms))
