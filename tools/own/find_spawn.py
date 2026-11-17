"""Read-only: where does the room data spawn an object? Reads the room listings local/analysis/ard-all/<room>.txt
(lane F's dump) and prints, for each object id given, every room / script / program whose spawn groups hold it,
with the count, the first place and the distance from that program's (or map program 0's) first PLAYER
placeholder (0x0236).
  python -I tools/own/find_spawn.py <objHex> [<objHex> ...] [--room hb08]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
D = ROOT / "local" / "analysis" / "ard-all"
want = [int(a, 16) for a in sys.argv[1:] if not a.startswith("--") and (sys.argv[sys.argv.index(a) - 1] != "--room")]
only = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
ENT = re.compile(r"\[\d+\] obj 0x([0-9A-F]{4}) pos \(([-0-9.]+), ([-0-9.]+), ([-0-9.]+)\)")
for f in sorted(D.glob("*.txt")):
    room = f.stem
    if only and room != only:
        continue
    scripts, groups = {}, {}          # scripts: (entry, program) -> [group names]; groups: name -> [(obj, x, y, z)]
    cur_entry = cur_prog = cur_group = None
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
        if m:
            cur_entry, kind = m.group(1), m.group(2)
            cur_prog = None
            cur_group = cur_entry if kind == "AreaDataSpawn" else None
            if cur_group:
                groups.setdefault(cur_group, [])
            continue
        m = re.match(r"Program 0x([0-9A-Fa-f]+)", line)
        if m:
            cur_prog = int(m.group(1), 16)
            scripts.setdefault((cur_entry, cur_prog), [])
            continue
        m = re.match(r'\s*Spawn "([^"]+)"', line)
        if m and cur_prog is not None:
            scripts[(cur_entry, cur_prog)].append(m.group(1))
            continue
        m = ENT.search(line)
        if m and cur_group:
            groups[cur_group].append((int(m.group(1), 16), float(m.group(2)), float(m.group(3)), float(m.group(4))))

    def player(prog):
        for key in (("map", prog), ("map", 0)):
            for g in scripts.get(key, []):
                for o, x, y, z in groups.get(g, []):
                    if o == 0x0236:
                        return (x, y, z)
        return None

    for (entry, prog), gl in sorted(scripts.items()):
        for g in gl:
            ents = groups.get(g, [])
            for w in want:
                hit = [e for e in ents if e[0] == w]
                if not hit:
                    continue
                pl = player(prog)
                dist = "?" if not pl else "%.0f" % min(((e[1] - pl[0]) ** 2 + (e[3] - pl[2]) ** 2) ** 0.5 for e in hit)
                has_map = ("map", prog) in scripts
                print("%s %-4s program %3d (0x%02X) group %-6s obj 0x%04X x%d nearest %s units from the hero's place%s" % (
                    room, entry, prog, prog, g, w, len(hit), dist, "" if has_map else " (no map program of that number)"))
