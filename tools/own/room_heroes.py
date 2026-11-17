"""For the missions that showed no hero in the sweep: where does a room place its heroes? Prints, for one room, every
spawn group that holds a PLAYER placeholder (0x0236) with its type and argument, and which map / battle / event
programs name that group. With a program number: also that program's own lines in the three scripts.
  python -I tools/own/room_heroes.py <room> [programDecimal]"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
room = sys.argv[1]
want = int(sys.argv[2]) if len(sys.argv) > 2 else None
progs = {"map": {}, "btl": {}, "evt": {}}
groups = {}
body = {}
sec = cur = grp = None
for line in (ROOT / "local" / "analysis" / "ard-all" / (room + ".txt")).read_text(encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
    if m:
        sec = m.group(1) if m.group(2) == "AreaDataScript" else None
        grp = m.group(1) if m.group(2) == "AreaDataSpawn" else None
        cur = None
        continue
    if sec in progs:
        m = re.match(r"Program 0x([0-9A-Fa-f]+)", line)
        if m:
            cur = int(m.group(1), 16)
            progs[sec][cur] = []
            body[(sec, cur)] = []
        elif cur is not None and line.strip():
            body[(sec, cur)].append(line.rstrip())
        m = re.search(r"Spawn \"?([A-Za-z0-9_]+)\"?", line)
        if m and cur is not None:
            progs[sec][cur].append(m.group(1))
    if grp:
        m = re.match(r"\s+\[\d+\] obj 0x0236 .* type (\d+) arg (\d+)", line)
        if m:
            groups.setdefault(grp, []).append((int(m.group(1)), int(m.group(2))))
print("room %s: map programs %s" % (room, " ".join(str(p) for p in sorted(progs["map"]))))
for g, pl in sorted(groups.items()):
    users = ["%s %d" % (s, p) for s in ("map", "btl", "evt") for p, gs in sorted(progs[s].items()) if g in gs]
    print("  group %-6s placeholder(s) %s  <- %s" % (g, ", ".join("type %d arg %d" % x for x in pl), "; ".join(users) or "no program names it"))
if want is not None:
    for s in ("map", "btl", "evt"):
        if (s, want) in body:
            print("  [%s program %d]" % (s, want))
            for l in body[(s, want)][:14]:
                print("     " + l[:110])
