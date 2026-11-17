"""Fourth pass of the mission sweep: for the missions given as room:program, a Type 1 jump whose three program
numbers are chosen so that the room HAS its heroes and the mission is NOT left at once (kit make_jumpkit2.py):
  battle = the mission's program;
  map    = the same number when the battle program's own groups hold a PLAYER placeholder and the map script
           has that number; else the first map program (0 first) whose groups hold a placeholder;
  event  = 0 when the event script has no program of that number, or when it has one that plays a scene or
           jumps away (SetEvent / SetJump: for the small numbers it is a story program that only shares the
           number); else the same number;
  entrance = the lowest "type 1" argument of the placeholder the map program brings (0 if the battle groups
           bring the heroes).
Writes local/sweep/list-q0.txt .. q3.txt ("room worldHex program NAME party map battle event entrance").
  python -I tools/own/sweep_lists4.py room:program [room:program ...]"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
ARD = ROOT / "local" / "analysis" / "ard-all"


def room_info(room):
    progs = {"map": {}, "btl": {}, "evt": {}}
    body, groups = {}, {}
    sec = cur = grp = None
    for line in (ARD / (room + ".txt")).read_text(encoding="utf-8", errors="replace").splitlines():
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
                body[(sec, cur)] = ""
            elif cur is not None:
                body[(sec, cur)] += line + "\n"
            m = re.search(r"Spawn \"?([A-Za-z0-9_]+)\"?", line)
            if m and cur is not None:
                progs[sec][cur].append(m.group(1))
        if grp:
            m = re.match(r"\s+\[\d+\] obj 0x0236 .* type (\d+) arg (\d+)", line)
            if m:
                groups.setdefault(grp, []).append((int(m.group(1)), int(m.group(2))))
    return progs, groups, body


miss = {}
for line in (SW / "missions.txt").read_text(encoding="utf-8").splitlines():
    h = line.split()
    if len(h) >= 5:
        miss[(h[0], h[2])] = h
out = []
for item in sys.argv[1:]:
    room, prog = item.split(":")
    h, p = miss[(room, prog)], int(prog)
    progs, groups, body = room_info(room)
    own = any(g in groups for g in progs["btl"].get(p, []))
    ent = 0
    if own and p in progs["map"]:
        pm = p
    else:
        cands = [q for q in sorted(progs["map"]) if any(g in groups for g in progs["map"][q])]
        pm = cands[0] if cands else (p if p in progs["map"] else 0)
        args = sorted(a for g in progs["map"].get(pm, []) for (t, a) in groups.get(g, []) if t == 1)
        if not own and args:
            ent = args[0]
    ev = body.get(("evt", p))
    pe = 0 if (ev is None or "SetJump" in ev or "SetEvent" in ev) else p
    out.append("%s %s %s %s %s %d %d %d %d" % (h[0], h[1], h[2], h[3], h[4], pm, p, pe, ent))
    print(out[-1], "  (heroes from the %s)" % ("battle groups" if own else "map program %d" % pm))
for i in range(4):
    (SW / ("list-q%d.txt" % i)).write_text("\n".join(out[i::4]) + ("\n" if out[i::4] else ""), encoding="utf-8", newline="\n")
print(len(out), "missions")
