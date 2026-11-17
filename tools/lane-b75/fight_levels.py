"""Lane B75: at which battle level is every boss entry fought, and what real HP does that give?

  python -I tools/lane-b75/fight_levels.py <laneC_ard_dir> <ai_ids.json> <enmp.bin> <lvpm.yml> <btlv.yml>
         <boss_entries.csv> <out.tsv> [percent] [levels.csv]

levels.csv (tools/lane-b75/data/boss_levels.csv) is the small data file the HP tool reads for its gauge cap:
entry_id, highest_level, source, placements.

Real HP = (HpMultiplier(level) * table value + 99) / 100   (VERIFIED, routine 0x001A0EE0).
Level of a fight: the entry's own fixed level if it has one; else the `BattleLevel N` command of the room program
that spawns the object; else the level of the world. The world level is the sum of the rows of the world-level
table (btlv) whose story flag is set; the upper bound used here is the sum of all rows except the two rows with
59 and 98 (flags 17 and 15), which give every world level 60 / 99 at once.

Output: one line per boss entry with every fight found (room:program mission level) and the largest real HP
before and after the change, so that entries which would pass the HP gauge's limit can be seen.
"""
import collections
import csv
import json
import os
import re
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

ard_dir, ai_json, enmp_bin, lvpm_yml, btlv_yml, list_csv, out = sys.argv[1:8]
percent = int(sys.argv[8]) if len(sys.argv) > 8 else 75
LIMIT = 3400

scan = json.load(open(ai_json, encoding="utf-8"))
ver, entries = parse(open(enmp_bin, "rb").read())
E = {e["id"]: e for e in entries}
mult = [int(m.group(1)) for m in re.finditer(r"HpMultiplier: (\d+)", open(lvpm_yml, encoding="utf-8").read())]

# world levels
rows, cur = [], None
for line in open(btlv_yml, encoding="utf-8"):
    m = re.match(r"^- Id: (\d+)", line)
    if m:
        cur = {}
        rows.append(cur)
        continue
    m = re.match(r"^  (\w+): (-?\d+)", line)
    if m and cur is not None:
        cur[m.group(1)] = int(m.group(2))
COL = {"al": "Agrabah", "bb": "BeastCastle", "ca": "PortRoyal", "dc": "DisneyCastle", "eh": "TheWorldThatNeverWas",
       "hb": "HollowBastion", "he": "OlympusColiseum", "lk": "PrideLands", "mu": "LandOfDragons",
       "nm": "HalloweenTown", "po": "HundredAcreWoods", "tr": "SpaceParanoids", "tt": "TwilightTown",
       "wi": "TimelessRiver", "zz": "WorldZZ", "es": "WorldOfDarkness", "di": "DestinyIslands", "lm": "Atlantica",
       "wm": "WorldMap"}
world_max = {}
for w, col in COL.items():
    world_max[w] = max(1, sum(r.get(col, 0) for r in rows if r.get(col, 0) not in (59, 98)))

obj_models = collections.defaultdict(list)
for model, r in scan.items():
    for o in r["objects"]:
        obj_models[int(o, 16)].append(model)

boss = {}
for row in csv.DictReader(open(list_csv, encoding="utf-8", newline="")):
    boss[int(row["entry_id"])] = row

fights = collections.defaultdict(list)     # entry id -> [(room, program, mission, level, source, model, lvl field)]
pat_ent = re.compile(r"ENT obj 0x([0-9A-Fa-f]+) .* arg (-?\d+) .* lvl (-?\d+)")
for fn in sorted(os.listdir(ard_dir)):
    if not fn.endswith(".txt"):
        continue
    room = fn[:-4]
    world = room[:2]
    spawns = collections.defaultdict(list)
    programs = []
    section, prog = None, None
    for line in open(os.path.join(ard_dir, fn), encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^==== entry (\S+) type (\S+)", line)
        if m:
            section, prog = (m.group(1), m.group(2)), None
            continue
        if section is None:
            continue
        if section[1] == "AreaDataScript":
            m = re.match(r"^Program (0x[0-9A-Fa-f]+)", line)
            if m:
                prog = {"script": section[0], "id": m.group(1), "mission": "", "level": None, "spawns": []}
                programs.append(prog)
                continue
            if prog is None:
                continue
            s = line.strip()
            m = re.match(r'^Mission \S+ "([^"]+)"', s)
            if m:
                prog["mission"] = m.group(1)
            m = re.match(r"^BattleLevel (\d+)", s)
            if m:
                prog["level"] = int(m.group(1))
            m = re.match(r'^Spawn "([^"]+)"', s)
            if m:
                prog["spawns"].append(m.group(1))
        elif section[1] == "AreaDataSpawn":
            m = pat_ent.search(line)
            if m:
                spawns[section[0]].append((int(m.group(1), 16), int(m.group(2)), int(m.group(3))))
    for pr in programs:
        level = pr["level"] if pr["level"] is not None else world_max.get(world, 50)
        src = "program" if pr["level"] is not None else "world"
        for sp in pr["spawns"]:
            for obj, arg, lvl in spawns.get(sp, []):
                for model in obj_models.get(obj, []):
                    for eid in scan[model]["valid"]:
                        if eid in boss:
                            fights[eid].append((room, pr["script"], pr["id"], pr["mission"], level, src, model, lvl))


def real(level, value):
    return (mult[level - 1] * value + 99) // 100


lines = []
over = 0
for eid in sorted(boss):
    e = E[eid]
    row = boss[eid]
    p = row["percent"].strip()
    pct = percent if p == "" else int(p)
    vals = [h for h in e["health"] if h > 0]
    top = max(vals)
    new_top = (top * (100 + pct) + 50) // 100
    fl = sorted(set(fights.get(eid, [])))
    if e["level"]:
        lv, why = e["level"], "fixed in the entry"
    elif fl:
        lv = max(f[4] for f in fl)
        why = "highest of %d placements" % len(fl)
    else:
        lv, why = 0, "NO PLACEMENT FOUND"
    old_hp = real(lv, top) if lv else 0
    new_hp = real(lv, new_top) if lv else 0
    # largest percent that still fits the limit at that level
    fit = pct
    if lv:
        while fit > 0 and real(lv, (top * (100 + fit) + 50) // 100) > LIMIT:
            fit -= 1
    flag = "OVER" if new_hp > LIMIT else ""
    over += bool(flag)
    places = collections.OrderedDict()
    for room, script, pid, mission, level, src, model, lvl in fl:
        places.setdefault("%s:%s:%s %s L%d(%s)%s" % (room, script, pid, mission or "-", level, src,
                                                    " lvl-field %d" % lvl if lvl else ""), None)
    lines.append([eid, row["names"] or row["objects"].split("[")[0], top, new_top, lv, why, old_hp, new_hp, flag, fit,
                  " | ".join(places)])

with open(out, "w", encoding="utf-8") as f:
    f.write("entry\tname\ttable value\tnew table value\thighest level\tlevel source\treal HP now\treal HP after\t"
            "over %d\tlargest percent that fits\tplacements\n" % LIMIT)
    for ln in lines:
        f.write("\t".join(str(x) for x in ln) + "\n")
if len(sys.argv) > 9:
    with open(sys.argv[9], "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry_id", "highest_level", "source", "placements"])
        for ln in lines:
            w.writerow([ln[0], ln[4], ln[5], ln[10]])
print("entries:", len(lines), "| over the limit at +%d %%:" % percent, over,
      "| no placement found:", sum(1 for ln in lines if ln[4] == 0))
print("world upper bounds:", " ".join("%s=%d" % kv for kv in sorted(world_max.items())))
