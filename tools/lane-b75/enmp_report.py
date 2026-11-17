"""Join the enemy parameter table with the object list: which objects use which entry, and the entry's values.

  python -I tools/lane-b75/enmp_report.py <enmp.bin> <objentry.txt> <out.tsv>
"""
import re
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

blob = open(sys.argv[1], "rb").read()
ver, entries = parse(blob)
by_id = {}
for e in entries:
    by_id.setdefault(e["id"], []).append(e)

objs = []
pat = re.compile(r"^0x([0-9A-F]+) type (\S+)\s+model (\S+)\s+anim (\S*)\s+flags 0x([0-9A-F]+) status (\d+) moveset (\d+)")
for line in open(sys.argv[2], encoding="utf-8", errors="replace"):
    m = pat.match(line)
    if m:
        objs.append({"obj": int(m.group(1), 16), "type": m.group(2), "model": m.group(3),
                     "status": int(m.group(6)), "moveset": int(m.group(7))})

users = {}
for o in objs:
    users.setdefault(o["status"], []).append(o)

with open(sys.argv[3], "w", encoding="utf-8") as f:
    f.write("enmp_index\tenmp_id\tlevel\thealth_nonzero\tmaxDamage\tminDamage\texp\tbonus\tobject_types\tobjects\n")
    for e in entries:
        hs = [(i, h) for i, h in enumerate(e["health"]) if h]
        us = users.get(e["id"], [])
        f.write("%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
            e["index"], e["id"], e["level"], " ".join("%d:%d" % x for x in hs), e["maxDamage"], e["minDamage"],
            e["exp"], e["bonus"], ",".join(sorted({u["type"] for u in us})),
            " ".join("%s(0x%X)" % (u["model"], u["obj"]) for u in us)))

ids = [e["id"] for e in entries]
print("version", ver, "entries", len(entries), "distinct ids", len(set(ids)), "id range", min(ids), max(ids))
print("duplicate ids:", sorted({i for i in ids if ids.count(i) > 1})[:20])
types = {}
for o in objs:
    types[o["type"]] = types.get(o["type"], 0) + 1
print("object types:", sorted(types.items(), key=lambda x: -x[1]))
no_entry = [o for o in objs if o["type"] in ("BOSS", "L_BOSS", "ZAKO", "L_ZAKO") and o["status"] not in by_id]
print("enemy-type objects whose status id has no table entry:", len(no_entry), [(o["model"], o["status"]) for o in no_entry[:12]])
mx = max((max(e["health"]), e["id"]) for e in entries)
print("largest single health value: %d (entry id %d)" % mx)
