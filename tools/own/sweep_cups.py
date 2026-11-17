"""The Olympus cups for the mission sweep. The cup rounds are not mission programs of their own: they are
"If Entrance N" blocks inside the battle programs of the arena room he09 (130 blocks), so the first list
(local/sweep/missions.txt, made from the un-indented Mission lines) does not have them.
This tool reads local/analysis/ard-all/he09.txt and writes
  local/sweep/missions-cups.txt   every block: "he09 06 <program>e<entrance> NAME party map battle event entrance"
  local/sweep/list-c0.txt .. c3   ONE block per mission name (the first one), split in four, for tools/own/sweep2.sh
The third field is a label (program, "e", entrance); the kit takes the numbers behind it.
  python -I tools/own/sweep_cups.py"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
text = (ROOT / "local" / "analysis" / "ard-all" / "he09.txt").read_text(encoding="utf-8", errors="replace").splitlines()
progs = {"map": set(), "evt": set()}
blocks = []
sec = prog = party = ent = None
for line in text:
    m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
    if m:
        sec = m.group(1) if m.group(2) == "AreaDataScript" else None
        prog = None
        continue
    if sec is None:
        continue
    m = re.match(r"Program 0x([0-9A-Fa-f]+)", line)
    if m:
        prog, party, ent = int(m.group(1), 16), "-", None
        if sec in progs:
            progs[sec].add(prog)
        continue
    if sec != "btl" or prog is None:
        continue
    m = re.match(r"Party (\S+)", line)
    if m:
        party = m.group(1)
    m = re.match(r"If Entrance (\d+)", line)
    if m:
        ent = int(m.group(1))
    if not line.strip():
        ent = None
    m = re.match(r"\s+Mission 0x[0-9A-Fa-f]+ \"([A-Z0-9_]+)\"", line)
    if m and ent is not None:
        blocks.append((prog, ent, m.group(1), party))
out, first = [], {}
for prog, ent, name, party in blocks:
    pm = prog if prog in progs["map"] else 0
    pe = prog if prog in progs["evt"] else 0
    line = "he09 06 %de%d %s %s %d %d %d %d" % (prog, ent, name, party, pm, prog, pe, ent)
    out.append(line)
    first.setdefault(name, line)
(SW / "missions-cups.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
one = list(first.values())
for i in range(4):
    (SW / ("list-c%d.txt" % i)).write_text("\n".join(one[i::4]) + "\n", encoding="utf-8", newline="\n")
print("%d blocks, %d mission names; map programs with a cup program: %d of %d" % (
    len(out), len(one), len({b[0] for b in blocks} & progs["map"]), len({b[0] for b in blocks})))
for l in one[:6]:
    print("  ", l)
