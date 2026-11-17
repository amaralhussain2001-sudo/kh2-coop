"""Scan all room dumps for battle programs that spawn enemies right away (candidates for a quick test fight).

  python -I tools/lane-b/find_fights.py [world-prefix]
Prints: room, program id, Party / Mission lines, enemy groups with counts, whether the same program id exists in
map and evt, and whether the player placeholder (0x236) sits in one of the spawned groups.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
objs = {}
for line in (ROOT / "local" / "analysis" / "objentry.txt").read_text().splitlines():
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = (m.group(2), m.group(3))

prefix = sys.argv[1] if len(sys.argv) > 1 else ""
for f in sorted((ROOT / "local" / "analysis-b" / "ard").glob(prefix + "*.txt")):
    text = f.read_text()
    entries = re.split(r"^==== entry ", text, flags=re.M)[1:]
    scripts, groups = {}, {}
    for e in entries:
        head, _, body = e.partition("\n")
        name, typ = head.split()[0], head.split()[2]
        if typ == "AreaDataScript":
            progs = {}
            for b in re.split(r"^(?=Program 0x)", body, flags=re.M):
                if b.strip():
                    progs[int(b.split()[1], 16)] = b
            scripts[name] = progs
        elif typ == "AreaDataSpawn":
            groups[name] = [int(x, 16) for x in re.findall(r"\] obj 0x([0-9A-F]+)", body)]
    for pid, b in sorted(scripts.get("btl", {}).items()):
        spawned = re.findall(r'^Spawn "([^"]+)"', b, flags=re.M)
        enemies = []
        has_player = False
        for g in spawned:
            ids = groups.get(g, [])
            z = [objs.get(i, ("?", "?"))[1] for i in ids if objs.get(i, ("?", "?"))[0] in ("ZAKO", "L_ZAKO")]
            if 0x236 in ids:
                has_player = True
            if z:
                enemies.append(f"{g}:{len(z)}x{'/'.join(sorted(set(z)))}")
        if not enemies:
            continue
        party = re.findall(r"^Party (\S+)", b, flags=re.M)
        mission = re.findall(r'^Mission \S+ "([^"]+)"', b, flags=re.M)
        other = [k for k in ("map", "evt") if pid in scripts.get(k, {})]
        evt_has_event = "SetEvent" in scripts.get("evt", {}).get(pid, "")
        print(f"{f.stem} prog 0x{pid:02X} ({pid}) party={party or '-'} mission={mission or '-'} "
              f"player_in_btl={has_player} also_in={other} evt_event={evt_has_event} :: {' '.join(enemies)}")
