"""Lane B75: write the boss table of the lane document (markdown) from the data files, so no number is typed by hand.

  python -I tools/lane-b75/make_doc_tables.py <boss_entries.csv> <fight_levels.tsv> <enmp.bin> <lvpm.yml> <out.md> [percent]
"""
import csv
import re
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

list_csv, levels_tsv, enmp_bin, lvpm_yml, out = sys.argv[1:6]
pct = int(sys.argv[6]) if len(sys.argv) > 6 else 75
LIMIT = 3400
ver, entries = parse(open(enmp_bin, "rb").read())
E = {e["id"]: e for e in entries}
mult = [int(m.group(1)) for m in re.finditer(r"HpMultiplier: (\d+)", open(lvpm_yml, encoding="utf-8").read())]
lv = {}
for i, line in enumerate(open(levels_tsv, encoding="utf-8")):
    if i:
        p = line.rstrip("\n").split("\t")
        lv[int(p[0])] = (int(p[4]), p[5], p[10])

# readable names where the community list has none (object names stay in the next column)
NAME = {24: "Possessor (inside Thresholder)", 72: "Shan-Yu's falcon", 79: "the cage (Timeless River)",
        102: "part of the Hydra fight", 115: "field object, Sark / MCP fight", 127: "Pete (cage chase, Timeless River)",
        131: "Leon (ally version only)", 139: "Tifa (ally version only)", 142: "Cloud (ally version only)",
        143: "Yuffie (ally version only)", 153: "field object, final Xemnas area", 172: "final dragon (Xemnas)",
        18: "Hades (story)", 196: "Hades (final fight / cups)", 177: "Hades (cups)", 78: "Axel (boss fight)",
        148: "Axel (first skirmish)", 124: "Grim Reaper (first fight)", 154: "Grim Reaper (second fight)",
        122: "Volcano Lord (story)", 123: "Blizzard Lord (story)", 197: "Volcano Lord (cups)", 198: "Blizzard Lord (cups)",
        19: "Cerberus (story)", 199: "Cerberus (cups)", 213: "Roxas (story / Final Mix fight)", 242: "Roxas (data rematch)",
        244: "Lingering Will (Terra)", 26: "Pete at Olympus (two missions)", 113: "Pete of the past",
        128: "Pete (Timeless River, final)", 179: "Pete (cups)", 130: "Riku (Land of Dragons)", 73: "Beast (as opponent)",
        90: "Xemnas (two fights)", 160: "Armored Xemnas", 239: "Xemnas, both forms (data rematch)",
        91: "the three hyenas (one entry)", 200: "Vexen (silhouette and data)", 214: "Lexaeus (silhouette and data)",
        215: "Marluxia (silhouette and data)", 216: "Larxene (silhouette and data)", 217: "Zexion (silhouette and data)"}


def real(level, v):
    return (mult[level - 1] * v + 99) // 100


rows = []
for r in csv.DictReader(open(list_csv, encoding="utf-8", newline="")):
    eid = int(r["entry_id"])
    e = E[eid]
    vals = [h for h in e["health"] if h > 0]
    p = r["percent"].strip()
    q = pct if p == "" else int(p)
    new = [(h * (100 + q) + 50) // 100 for h in vals]
    level, why, places = lv[eid]
    if e["level"]:
        level = e["level"]
    cap = (100 * LIMIT) // mult[level - 1]
    capped = [min(n, max(h, cap)) for h, n in zip(vals, new)]
    name = NAME.get(eid) or r["names"] or r["objects"].split("[")[0]
    objs = " ".join(sorted({o.split("[")[0] for o in r["objects"].replace("| also:", " ").split() if "[" in o}))
    lvl = ("%d fixed" % level) if e["level"] else str(level)
    if q == 0:
        rows.append("| %d | %s | %s | %s | unchanged | %s | %d | unchanged | unchanged |" % (
            eid, name, objs, " ".join(map(str, vals)), lvl, real(level, max(vals))))
        continue
    r_old, r_new, r_cap = real(level, max(vals)), real(level, max(new)), real(level, max(capped))
    cap_txt = "same" if capped == new else "%s (HP %d, +%d %%)" % (" ".join(map(str, capped)), r_cap,
                                                                    round(100 * max(capped) / max(vals)) - 100)
    rows.append("| %d | %s | %s | %s | %s | %s | %d | %d%s | %s |" % (
        eid, name, objs, " ".join(map(str, vals)), " ".join(map(str, new)), lvl, r_old, r_new,
        " **over**" if r_new > LIMIT else "", cap_txt))

head = ("| entry | boss | objects | table health now | table health +%d %% | highest level | real HP there now | "
        "real HP there +%d %% | with the gauge cap instead |\n|---|---|---|---|---|---|---|---|---|\n" % (pct, pct))
open(out, "w", encoding="utf-8", newline="\n").write(head + "\n".join(rows) + "\n")
print("rows", len(rows), "->", out)
