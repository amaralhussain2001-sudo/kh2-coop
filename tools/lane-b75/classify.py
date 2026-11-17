"""Build the list of enemy-table entries (ENMP ids) used by boss objects, and flag the doubtful ones.

Inputs: the AI-script scan (ai_ids.json), the enemy table, the community name list (names only, as a reading aid).
Output: boss_entries.tsv (one row per entry id) and a summary on screen.

  python -I tools/lane-b75/classify.py <ai_ids.json> <enmp.bin> <khbr_enemies.tsv> <out.tsv>
"""
import collections
import json
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

scan = json.load(open(sys.argv[1], encoding="utf-8"))
ver, entries = parse(open(sys.argv[2], "rb").read())
E = {e["id"]: e for e in entries}

names = collections.defaultdict(list)       # model -> community names
kh_type = {}
kh_idx = collections.defaultdict(set)       # model -> community entry index
for i, line in enumerate(open(sys.argv[3], encoding="utf-8")):
    if i == 0:
        continue
    name, typ, model, obj, idx, enabled, var = line.rstrip("\n").split("\t")
    names[model].append(name)
    kh_type[model] = typ
    try:
        kh_idx[model].add(int(idx, 0))
    except ValueError:
        pass

users = collections.defaultdict(list)
for model, r in scan.items():
    for i in r["valid"]:
        users[i].append(model)

BOSS = ("BOSS", "L_BOSS")
rows = []
for eid in sorted(users):
    us = users[eid]
    boss_users = [m for m in us if any(t in BOSS for t in scan[m]["types"])]
    other_users = [m for m in us if m not in boss_users]
    if not boss_users:
        continue
    e = E[eid]
    rows.append({"id": eid, "level": e["level"], "health": [(i, h) for i, h in enumerate(e["health"]) if h],
                 "boss_users": boss_users, "other_users": other_users,
                 "names": sorted({n for m in boss_users for n in names.get(m, [])}),
                 "max_dmg": e["maxDamage"], "min_dmg": e["minDamage"]})

with open(sys.argv[4], "w", encoding="utf-8") as f:
    f.write("entry_id\tfixed_level\thealth_values\tboss_objects\tother_objects_using_it\tcommunity_names\n")
    for r in rows:
        f.write("%d\t%d\t%s\t%s\t%s\t%s\n" % (r["id"], r["level"], " ".join("%d:%d" % x for x in r["health"]),
                " ".join("%s[%s]" % (m, ",".join(scan[m]["types"])) for m in r["boss_users"]),
                " ".join("%s[%s]" % (m, ",".join(scan[m]["types"])) for m in r["other_users"]),
                "; ".join(r["names"])))

print("entries used by at least one BOSS / L_BOSS object:", len(rows))
print("  of them also used by a non-boss object:", [(r["id"], r["other_users"]) for r in rows if r["other_users"]])
print("  with more than one health value (parts or phases):", [(r["id"], r["health"]) for r in rows if len(r["health"]) > 1])
print("  with a fixed level:", [(r["id"], r["level"]) for r in rows if r["level"]])
mx = max(r["health"][0][1] for r in rows)
print("  largest boss health value:", mx, "-> x1.75 =", (mx * 175 + 50) // 100)
# community cross-check
agree = disagree = 0
for model, idxs in kh_idx.items():
    if model in scan and idxs - {999}:
        mine = set(scan[model]["valid"])
        if (idxs - {999}) <= mine:
            agree += 1
        else:
            disagree += 1
            print("  community list differs for", model, "theirs", sorted(idxs - {999}), "mine", sorted(mine))
print("community cross-check: same entry for %d models, different for %d" % (agree, disagree))
# boss-typed objects with a script but no entry, and boss-typed objects without script
no_entry = [m for m, r in scan.items() if any(t in BOSS for t in r["types"]) and not r["valid"]]
print("boss-typed scripts that set no valid entry:", no_entry)
# story fights that the community calls bosses but whose object is not typed BOSS
extra = [(m, scan[m]["types"], scan[m]["valid"], names[m]) for m in scan
         if kh_type.get(m) == "boss" and not any(t in BOSS for t in scan[m]["types"])]
print("community 'boss' whose object type is not BOSS:", extra)
