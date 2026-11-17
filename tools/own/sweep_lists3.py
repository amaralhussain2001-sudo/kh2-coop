"""Third pass of the mission sweep: list the missions that still have no hero on screen (class NO-HERO or a wrong
room) and work out, from the decoded room files (local/analysis/ard-all/<room>.txt), a Type 1 jump with three
separate program numbers (tools/own/make_jumpkit2.py):
  battle = the mission's program;
  map    = the same number if the room's map programs have it; else the map program of a sister program (another
           program of the same room with the same mission name); else the room's map program 0 (else its lowest);
  event  = the same number if the event programs have it, else 0;
  entrance = the lowest "type 1" argument of a PLAYER placeholder (0x0236) in the spawn groups of that map program
             (0 if none is found).
Writes local/sweep/list-z.txt: "room worldHex program NAME party map battle event entrance" and prints the lines.
  python -I tools/own/sweep_lists3.py [room:program ...]      (with arguments: only these missions)"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
ARD = ROOT / "local" / "analysis" / "ard-all"


def room_info(room):
    progs = {"map": {}, "btl": {}, "evt": {}}
    groups = {}
    sec = cur = grp = None
    for line in (ARD / (room + ".txt")).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
        if m:
            sec = m.group(1) if m.group(2) == "AreaDataScript" else None
            grp = m.group(1) if m.group(2) == "AreaDataSpawn" else None
            cur = None
            if grp:
                groups[grp] = []
            continue
        if sec in progs:
            m = re.match(r"Program 0x([0-9A-Fa-f]+)", line)
            if m:
                cur = int(m.group(1), 16)
                progs[sec][cur] = []
            m = re.match(r"\s*Spawn \"?([A-Za-z0-9_]+)\"?", line)
            if m and cur is not None:
                progs[sec][cur].append(m.group(1))
        if grp:
            m = re.match(r"\s+\[\d+\] obj 0x0236 .* type (\d+) arg (\d+)", line)
            if m:
                groups[grp].append((int(m.group(1)), int(m.group(2))))
    return progs, groups


want = set(sys.argv[1:])
rep = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "own" / "sweep_report.py")], capture_output=True, text=True).stdout
todo = []
for line in rep.splitlines():
    h = line.split()
    if len(h) > 5 and re.fullmatch(r"[a-z]{2}\d\d", h[0]) and ("NO-HERO" in line or "WRONG-ROOM" in line or "NO-PROBE" in line):
        todo.append((h[0], h[1]))
# no third run for the games that have no hero object by design or are covered by the special-mode batches
# (Atlantica musicals, Hunny Slider / Pot, the toy cannon, the carpet room, the Light Cycle's later phases)
todo = [(r, p) for (r, p) in todo if not (r[:2] == "lm" or r in ("po07", "po08", "nm10", "al14", "tr02"))]
if want:
    todo = [tuple(x.split(":")) for x in want]
miss = {}
for line in (SW / "missions.txt").read_text(encoding="utf-8").splitlines():
    h = line.split()
    if len(h) >= 5:
        miss[(h[0], h[2])] = h
out = []
for room, prog in todo:
    h = miss[(room, prog)]
    p = int(prog)
    progs, groups = room_info(room)
    sisters = [int(k[1]) for k, v in miss.items() if k[0] == room and v[3] == h[3] and int(k[1]) != p and int(k[1]) in progs["map"]]
    pm = p if p in progs["map"] else (sisters[0] if sisters else (0 if 0 in progs["map"] else (min(progs["map"]) if progs["map"] else 0)))
    pe = p if p in progs["evt"] else 0
    ents = sorted(a for g in progs["map"].get(pm, []) for (t, a) in groups.get(g, []) if t == 1)
    ent = ents[0] if ents else 0
    out.append("%s %s %s %s %s %d %d %d %d" % (h[0], h[1], h[2], h[3], h[4], pm, p, pe, ent))
    print(out[-1], "   (map programs with it: %s; groups of map %d: %s)" % ("yes" if p in progs["map"] else "no", pm, ",".join(progs["map"].get(pm, []))))
(SW / "list-z.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(len(out), "missions")
