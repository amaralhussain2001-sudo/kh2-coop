"""From the decoded AI scripts: which enemy-table entry (ENMP id) does each object give itself, and what else
do the scripts do with HP.

The script call `syscall 2, 9 ; trap_btlobj_set_sheet (3 in)` takes (object, entry id, flag); the id is the
push two lines above the call. (VERIFIED: handler 0x0018F1C0 -> 0x001B3C00 -> 0x001A1018 -> table lookup 0x001DB5A8.)

  python -I tools/lane-b75/scan_ai.py <aiDir> <objentry.txt> <enmp.bin> <outDir>
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

aidir, objtxt, enmpbin, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
ver, entries = parse(open(enmpbin, "rb").read())
E = {e["id"]: e for e in entries}

pat = re.compile(r"^0x([0-9A-F]+) type (\S+)\s+model (\S+)\s+anim (\S*)\s+flags 0x([0-9A-F]+) status (\d+)")
objs = collections.defaultdict(list)
for line in open(objtxt, encoding="utf-8", errors="replace"):
    m = pat.match(line)
    if m:
        objs[m.group(3)].append({"obj": int(m.group(1), 16), "type": m.group(2), "status": int(m.group(6))})

push = re.compile(r"^\s*push (-?\d+)\s*$")
per_model = {}
hp_calls = collections.defaultdict(lambda: collections.Counter())
abs_hp = []
for fn in sorted(os.listdir(aidir)):
    if not fn.endswith(".txt"):
        continue
    model = fn[:-4]
    lines = open(os.path.join(aidir, fn), encoding="utf-8", errors="replace").read().split("\n")
    ids, computed, dup = [], 0, 0
    for i, l in enumerate(lines):
        if "trap_btlobj_set_sheet" in l:
            m = push.match(lines[i - 2]) if i >= 2 else None
            if m:
                ids.append(int(m.group(1)))
            else:
                computed += 1
        if "trap_btlobj_dup_sheet" in l:
            dup += 1
        for name in ("trap_sheet_set_hp", "trap_sheet_set_min_hp", "trap_sheet_hp_rate", "trap_sheet_hp ", "trap_sheet_max_hp",
                     "trap_sheet_min_hp"):
            if name in l:
                hp_calls[model][name.strip()] += 1
        if "trap_sheet_set_hp" in l or "trap_sheet_set_min_hp" in l:
            ctx = [x.strip() for x in lines[max(0, i - 6):i]]
            abs_hp.append((model, l.strip().split(";")[1].split("(")[0].strip(), ctx))
    per_model[model] = {"ids": ids, "computed": computed, "dup": dup}

users = collections.defaultdict(list)
for model, d in per_model.items():
    for i in sorted(set(d["ids"])):
        users[i].append(model)

with open(os.path.join(out, "model_entries.tsv"), "w", encoding="utf-8") as f:
    f.write("model\tobject_types\tobject_ids\tstatus\tentry_ids\tcomputed_calls\tdup_calls\n")
    for model in sorted(per_model):
        d = per_model[model]
        o = objs.get(model, [])
        f.write("%s\t%s\t%s\t%s\t%s\t%d\t%d\n" % (
            model, ",".join(sorted({x["type"] for x in o})), " ".join("0x%X" % x["obj"] for x in o),
            " ".join(str(x["status"]) for x in o), " ".join(map(str, d["ids"])), d["computed"], d["dup"]))

with open(os.path.join(out, "entry_users.tsv"), "w", encoding="utf-8") as f:
    f.write("entry_id\tlevel\thealth\tuser_types\tusers\n")
    for e in entries:
        us = users.get(e["id"], [])
        types = collections.Counter(t for m in us for t in {x["type"] for x in objs.get(m, [])})
        hs = " ".join("%d:%d" % (i, h) for i, h in enumerate(e["health"]) if h)
        f.write("%d\t%d\t%s\t%s\t%s\n" % (e["id"], e["level"], hs, ",".join("%s=%d" % x for x in sorted(types.items())), " ".join(us)))

json.dump({"per_model": per_model, "users": {str(k): v for k, v in users.items()}},
          open(os.path.join(out, "ai_scan.json"), "w", encoding="utf-8"), indent=1)

with open(os.path.join(out, "hp_script_calls.txt"), "w", encoding="utf-8") as f:
    for model in sorted(hp_calls):
        f.write("%s\t%s\n" % (model, ", ".join("%s x%d" % x for x in sorted(hp_calls[model].items()))))
    f.write("\n== contexts of set_hp / set_min_hp ==\n")
    for model, name, ctx in abs_hp:
        f.write("%s %s | %s\n" % (model, name, " ; ".join(ctx)))

n_models = len(per_model)
with_ids = sum(1 for d in per_model.values() if d["ids"])
print("scripts", n_models, "with a constant set_sheet", with_ids, "with a computed id", sum(1 for d in per_model.values() if d["computed"]),
      "with dup_sheet", sum(1 for d in per_model.values() if d["dup"]))
print("table entries used by some script:", len(users), "of", len(entries), "| ids used but missing in table:", sorted(set(users) - set(E)))
unused = [e["id"] for e in entries if e["id"] not in users]
print("entries no script names:", unused)
