"""READ-ONLY study tool (eighth round, plan row 9): which boss scripts use a PAIRED MOVE (trap_obj_motion_capture),
in which rooms their objects stand, and what the mission sweep of the seventh round said about those rooms.
  python -I tools/own/row9_map.py            -> a plain table on the screen
  python -I tools/own/row9_map.py --json     -> the same as JSON (for row9_report.py)
Sources: local/analysis/boss-survey.txt (boss_survey.py), local/analysis/objentry.txt, local/analysis/ard-all/*.txt
(the decoded room files), docs/PARITY-SWEEP.md (sweep_doc.py). The room match is BY ROOM: a room file names the
object in one of its spawn groups; which of the room's programs uses that group is not followed here."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
AN = ROOT / "local" / "analysis"


def scripts():
    out = []
    for line in (AN / "boss-survey.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"(B_\S+)\s+player\s+(\d+)\s+hold\s+(\S+)\s+pad\s+(\S+)", line)
        if not m:
            continue
        hold = m.group(3).split(",")
        if "trap_obj_motion_capture" in hold:
            out.append((m.group(1), int(m.group(2)), hold, m.group(4)))
    return out


def objects():
    ids = {}
    kinds = {}
    for line in (AN / "objentry.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"0x([0-9A-Fa-f]{4}) type (\S+)\s+model (\S+)", line)
        if m:
            ids.setdefault(m.group(3), []).append(int(m.group(1), 16))
            kinds[m.group(3)] = m.group(2)
    return ids, kinds


def rooms():
    where = {}
    for f in sorted((AN / "ard-all").glob("*.txt")):
        for m in re.finditer(r"obj 0x([0-9A-Fa-f]{4}) ", f.read_text(encoding="utf-8", errors="replace")):
            where.setdefault(int(m.group(1), 16), set()).add(f.stem)
    return where


def sweep():
    rows = {}
    for line in (ROOT / "docs" / "PARITY-SWEEP.md").read_text(encoding="utf-8", errors="replace").splitlines():
        c = [x.strip() for x in line.split("|")]
        if len(c) < 7 or not re.match(r"[a-z]{2}\d\d \d+$", c[3]):
            continue
        room, prog = c[3].split()
        rows.setdefault(room, []).append({"mission": c[2].strip("`"), "program": int(prog), "result": c[4], "faults": c[5]})
    return rows


def main():
    ids, kinds = objects()
    where = rooms()
    sw = sweep()
    table = []
    for name, asks, hold, pad in scripts():
        rs = sorted({r for i in ids.get(name, []) for r in where.get(i, ())})
        table.append({"script": name, "kind": kinds.get(name, "?"), "ids": ["%04X" % i for i in ids.get(name, [])],
                      "rooms": rs, "sweep": {r: sw.get(r, []) for r in rs},
                      "capture_form": "trap_player_capture_form" in hold, "pad": pad})
    if "--json" in sys.argv:
        print(json.dumps(table, indent=1))
        return
    for t in table:
        print("%-20s %-7s ids %-14s rooms %s" % (t["script"], t["kind"], ",".join(t["ids"]) or "-", ",".join(t["rooms"]) or "-"))
        for r in t["rooms"]:
            for s in t["sweep"][r]:
                print("      %s %3d %-20s %-10s faults %s" % (r, s["program"], s["mission"], s["result"], s["faults"]))
    print("scripts with a paired move:", len(table), "| with an object number:", sum(1 for t in table if t["ids"]),
          "| found in a room:", sum(1 for t in table if t["rooms"]))


main()
