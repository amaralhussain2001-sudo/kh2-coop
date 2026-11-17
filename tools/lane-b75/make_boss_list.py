"""Write the reviewable boss list: tools/lane-b75/data/boss_entries.csv.

Rule (see docs/lanes/B75-boss-hp.md): an enemy-table entry (ENMP id) counts as a boss entry when the AI script of
an object that the game's own object list types BOSS or L_BOSS gives itself that entry. Entries with a manual
decision below are kept in the list with percent 0 and the reason, so nothing is hidden.

Columns: entry_id, percent (empty = the build's one number; 0 = left as in the original; another number = that
percent for this entry only), decision, names (community names, reading aid only), objects, health (original
values, index:value), note.

  python -I tools/lane-b75/make_boss_list.py <ai_ids.json> <enmp.bin> <khbr_enemies.tsv> <placements.json> <out.csv>
"""
import collections
import csv
import json
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

scan = json.load(open(sys.argv[1], encoding="utf-8"))
ver, entries = parse(open(sys.argv[2], "rb").read())
E = {e["id"]: e for e in entries}
names = collections.defaultdict(list)
for i, line in enumerate(open(sys.argv[3], encoding="utf-8")):
    if i:
        p = line.rstrip("\n").split("\t")
        names[p[2]].append(p[0])
placed = json.load(open(sys.argv[4], encoding="utf-8"))

BOSS = ("BOSS", "L_BOSS")
# Manual decisions. Each one is explained in the document, section "Doubtful cases".
SKIP = {
    79: "the cage in 'Break the cage before Pete escapes!' (WI02_MS103): an object, in a race against a gauge",
    131: "only placed user is ally Leon (N_HB530_BTL, rooms hb08/hb16); the BOSS-typed twin object is in no room",
    139: "only placed user is ally Tifa (N_HB570_BTL, room hb16); the BOSS-typed twin object is in no room",
    142: "only placed user is ally Cloud (N_HB550_BTL, room hb16); the BOSS-typed twin object is in no room",
    143: "only placed user is ally Yuffie (N_HB580_BTL, room hb16); the BOSS-typed twin object is in no room",
}
NOTE = {
    15: "also set by the toy version N_NM050_BTL_TOY (Gift Wrapping); its script never reads HP (min HP 1)",
    16: "also set by the toy version N_NM060_BTL_TOY (Gift Wrapping); its script never reads HP (min HP 1)",
    17: "also set by the toy version N_NM070_BTL_TOY (Gift Wrapping); its script never reads HP (min HP 1)",
    18: "Hades: used by three Hades objects (first meeting, escape, final fight)",
    26: "Pete at Olympus: HE08_MS107 has a 90 s limit, HE08_MS106 is 'defend Megara'",
    71: "Shan-Yu: 'guarding the gates' mission with a gate gauge",
    72: "Shan-Yu's falcon (object B_MU110), same fight",
    78: "Axel (second fight); also set by the ally version B_EX110_FRIEND, which gets the same +HP",
    88: "Demyx: the fight has timed water-form phases (60 s, 10 forms); the forms are not changed",
    89: "Luxord: fight with time gauges",
    91: "the three hyenas (one entry for all three); LK02_MS102 is a 'protect Pumbaa and Timon' mission",
    113: "Past Pete; also set by the non-boss version N_WI010_BTL",
    115: "object F_TR050 typed BOSS in the Sark / MCP fight (tr09)",
    127: "Pete in the cage chase (WI02_MS103); the cage itself (79) is left unchanged",
    153: "object F_EH100 typed BOSS",
    172: "final dragon: only its five part values are read by its script",
    200: "Vexen: second value (100) is read as its own HP pool; meaning not checked in play",
    243: "Luxord (data rematch): fight with time gauges",
    244: "Lingering Will: second value (50) is read as its own HP pool; meaning not checked in play",
}

users = collections.defaultdict(list)
for model, r in scan.items():
    for i in r["valid"]:
        users[i].append(model)


def is_placed(model):
    return any(placed.get(o, {}).get("rooms") for o in scan[model]["objects"])


rows = []
for eid in sorted(users):
    boss_users = [m for m in users[eid] if any(t in BOSS for t in scan[m]["types"])]
    if not boss_users:
        continue
    other = [m for m in users[eid] if m not in boss_users]
    e = E[eid]
    nm = sorted({n for m in boss_users for n in names.get(m, [])})
    objs = " ".join("%s[%s%s]" % (m, "/".join(scan[m]["types"]), "" if is_placed(m) else ", in no room") for m in boss_users)
    if other:
        objs += " | also: " + " ".join("%s[%s]" % (m, "/".join(scan[m]["types"])) for m in other)
    health = " ".join("%d:%d" % (i, h) for i, h in enumerate(e["health"]) if h)
    if eid in SKIP:
        rows.append([eid, 0, "left unchanged", "; ".join(nm), objs, health, SKIP[eid]])
    else:
        note = NOTE.get(eid, "")
        if e["level"]:
            note = ("fixed level %d. " % e["level"]) + note
        rows.append([eid, "", "boss", "; ".join(nm), objs, health, note.strip()])

with open(sys.argv[5], "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["entry_id", "percent", "decision", "names", "objects", "health", "note"])
    w.writerows(rows)
print("rows", len(rows), "| boss", sum(1 for r in rows if r[2] == "boss"), "| left unchanged", sum(1 for r in rows if r[2] != "boss"))
