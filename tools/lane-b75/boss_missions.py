"""Which missions hold boss objects, and which of those run against a timer, counter or gauge.

  python -I tools/lane-b75/boss_missions.py <mission_facts.json> <ai_ids.json> <boss_ids.txt> <out.tsv>
boss_ids.txt: one enemy-table id per line (the entries that will be scaled).
"""
import json
import sys

facts = json.load(open(sys.argv[1], encoding="utf-8"))
scan = json.load(open(sys.argv[2], encoding="utf-8"))
boss_ids = {int(x.split()[0]) for x in open(sys.argv[3], encoding="utf-8") if x.strip() and not x.startswith("#")}

rows = []
for name in sorted(facts):
    m = facts[name]
    objs = m.get("objects", {})
    models = {}
    for typ, d in objs.items():
        for model, n in d.items():
            models[model] = (typ, n)
    scaled = {}
    for model, (typ, n) in models.items():
        ids = set(scan.get(model, {}).get("valid", [])) & boss_ids
        if ids:
            scaled[model] = (typ, n, sorted(ids))
    boss_typed = [mo for mo, (typ, n) in models.items() if typ in ("BOSS", "L_BOSS")]
    if not scaled and not boss_typed and "boss" not in m.get("flags", ""):
        continue
    meters = []
    for op, args in m.get("ops", []):
        if op in ("Timer", "Counter", "Gauge"):
            meters.append("%s(%s)" % (op, ",".join(str(a) for a in args)))
    rows.append((name, m.get("world", ""), m.get("info_text", ""), m.get("flags", ""), " ".join(meters),
                 " ".join("%s[%s x%d -> %s]" % (mo, t, n, "/".join(map(str, i))) for mo, (t, n, i) in sorted(scaled.items())),
                 " ".join(mo for mo in boss_typed if mo not in scaled), " ".join(m.get("programs", []))))

with open(sys.argv[4], "w", encoding="utf-8") as f:
    f.write("mission\tworld\tobjective_text\tflags\tmeters\tscaled_objects\tboss_typed_not_scaled\tprograms\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print("missions with boss objects or the boss flag:", len(rows))
print("  with scaled objects:", sum(1 for r in rows if r[5]))
print("  with scaled objects AND a timer:", sum(1 for r in rows if r[5] and "Timer" in r[4]))
print("  with scaled objects AND any meter:", sum(1 for r in rows if r[5] and r[4]))
print("  boss flag but nothing scaled:", sum(1 for r in rows if not r[5]))
