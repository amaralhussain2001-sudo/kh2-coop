"""Lane P: extra counts and names for the game-wide part of the audit. Writes local/analysis/lane-p/extras.txt"""
import collections
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
LC = ROOT / "local" / "analysis" / "lane-c"
OUT = ROOT / "local" / "analysis" / "lane-p"

objs = {}
for line in (ROOT / "local" / "analysis" / "objentry.txt").read_text(encoding="utf-8", errors="replace").split("\n"):
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = (m.group(2), m.group(3))

by_type = collections.Counter()
models = collections.defaultdict(collections.Counter)
rooms_of = collections.defaultdict(set)
for f in sorted((LC / "ard").glob("*.txt")):
    for line in f.read_text(encoding="utf-8", errors="replace").split("\n"):
        m = re.match(r"\s+ENT obj 0x([0-9A-Fa-f]+)", line)
        if m:
            t, model = objs.get(int(m.group(1), 16), ("?", "?"))
            by_type[t] += 1
            models[t][model] += 1
            rooms_of[model].add(f.stem)

out = ["== placed entities by object type (all 289 rooms)"]
for t, n in by_type.most_common():
    out.append(f"{t}: {n}")
for t in ("TREASURE", "JIGSAW", "SHOP", "MEMO", "SUBMENU", "WORLDMAP", "MINIGAME", "SP", "PRIZEBOX", "MASSEFFECT", "E_OBJ", "BTLNPC"):
    if t in models:
        out.append(f"== {t} models: " + ", ".join(f"{k}x{v}" for k, v in models[t].most_common(40)))
out.append("== object types in the object list: " + ", ".join(f"{k} {v}" for k, v in collections.Counter(t for t, _ in objs.values()).most_common()))
for pat in ("SKATE", "SAVE", "MOOGLE", "PO0", "AL14", "GUMI", "LM1", "SIDECAR", "CARPET", "LIGHTCYCLE", "DICE", "CARD", "STRUGGLE", "TT08", "P_EX2", "P_EX3", "H_ZZ"):
    hit = sorted({f"{m}({t})" for t, m in objs.values() if pat in m})
    out.append(f"== object models containing {pat}: " + ", ".join(hit[:60]))
    used = sorted({m for t, m in objs.values() if pat in m and rooms_of.get(m)})
    if used:
        out.append("   placed in rooms: " + "; ".join(f"{m}: {' '.join(sorted(rooms_of[m]))}" for m in used[:30]))


def load(name):
    d = {}
    p = OUT / "msg" / (name + ".tsv")
    for line in p.read_text(encoding="utf-8").split("\n"):
        k, _, v = line.partition("\t")
        if k.isdigit():
            d[int(k)] = re.sub(r"\s+", " ", re.sub(r"\{:[^}]*\}", " ", v.replace(" / ", " "))).strip()
    return d


for name, pats in (("gumi", ["Sweep", "Storm", "Highway", "Island", "Dreadnought", "Mission", "Route"]),
                   ("lm", ["Swim This Way", "Part of Your World", "Under the Sea", "Ursula", "New Day", "Chapter", "musical", "Musical"]),
                   ("po", ["Blustery", "Hunny", "Balloon", "Expotition", "Slider", "Pot"]),
                   ("sys", ["Cup", "Struggle", "Skateboard", "Puzzle", "Mushroom", "Paradox", "Gummi", "Synthes", "Moogle"]),
                   ("tt", ["Struggle", "Mail Delivery", "Cargo", "Grandstander", "Poster", "Bee", "Junk", "Skateboard", "job", "Job"]),
                   ("he", ["Cup", "Tournament", "Round"]),
                   ("jm", ["Minigame", "Mini-game", "Mushroom"])):
    d = load(name)
    seen = []
    for k in sorted(d):
        v = d[k]
        if 2 < len(v) < 90 and any(p in v for p in pats):
            seen.append(f"{k}:{v}")
    out.append(f"== text file {name} ({len(d)} messages), short lines matching {pats}: " + " | ".join(seen[:70]))
(OUT / "extras.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("ok", len(out))
