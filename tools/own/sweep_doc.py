"""Write docs/PARITY-SWEEP.md: the result of the mission sweep (seventh round) in the story order of
docs/PARITY-CHECKLIST.md. One line per mission program: the checklist row, the mission name, the program number,
the result class and the three probe points. Hand-written notes come from docs/PARITY-SWEEP-NOTES.txt
(lines "room program | class | note"; a class there replaces the automatic one).

  python -I tools/own/sweep_doc.py
Reads local/sweep/*.log (the last line of a mission wins), local/sweep/missions.txt, docs/PARITY-CHECKLIST.md.
"""
import collections
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
DOCS = ROOT / "docs"
WORLD = {"tt": 2, "hb": 4, "bb": 5, "he": 6, "al": 7, "mu": 8, "po": 9, "lk": 10, "lm": 11, "dc": 12, "wi": 13,
         "nm": 14, "wm": 15, "ca": 16, "tr": 17, "eh": 18, "es": 1, "zz": 0, "dh": 3}
WORDS = {
    "OK": "works: both heroes there, in sync, 0 fault lines",
    "OK-V5": "works with disc v5: player 2 has his own special object",
    "SHARED": "one hero, both controllers drive him (twenty-eighth glue)",
    "P2-NONE": "player 2 has no hero",
    "NO-HERO": "no hero on screen in this test start",
    "WRONG-ROOM": "the test jump did not reach the room",
    "FAULT": "fault lines",
    "DESYNC": "OUT OF SYNC",
    "NO-END": "the session did not close",
    "NO-PROBE": "no probe line",
    "OK-GAME": "works with two heroes; its fault lines are there with no patch too (the game's own in this test start)",
    "TEST-LIMIT": "cannot be started by a jump test (see the note)",
    "SCENE": "a scene or a mission without play at its start (see the note)",
    "CUP-LOBBY": "a cup round that was over before the first probe point (level 1 heroes); both heroes then stand in the cup lobby with two views, in sync",
}

rows = {}
for log in sorted(SW.glob("*.log")):
    for line in log.read_bytes().decode("utf-8", "replace").replace(chr(13) + " | ", " | ").splitlines():
        parts = line.split(" | ")
        head = parts[0].split()
        if len(head) >= 5 and len(parts) >= 3:
            rows[(head[0], head[2])] = (head, parts, log.name)

notes = {}
nf = DOCS / "PARITY-SWEEP-NOTES.txt"
if nf.exists():
    for line in nf.read_text(encoding="utf-8").splitlines():
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 3 and not line.startswith("#"):
            k = tuple(p[0].split()[:2])
            notes[k] = (p[1], p[2])


MSN = {0x1BAD04, 0x1BAD10, 0x1BAD40, 0x1BAD64, 0x1BAD88, 0x1BAED8, 0x1BAF74, 0x1BAFA8, 0x1BB978, 0x1BB9C8, 0x1BBF20,
       0x1BBF60, 0x1BC154, 0x1DB610}
CONT = {0x1AEBF0, 0x19499C, 0x1A9110, 0x1AFC54, 0x194A1C}
ATT = {0x1C0DF0, 0x1C0E00, 0x1880B0, 0x1880D4, 0x1C0CD8, 0x171444}
GAUGE = {0x155EF4, 0x155F54, 0x15601C, 0x15603C, 0x1A1DE0}
GAME_KINDS = {"msn"}
KIND_WORDS = {
    "msn": "the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)",
    "continue": "Continue on a jump disc (the game's own test limit, fifth round)",
    "attach": "a script attaches something to an object that is not there after a jump start",
    "gauge": "player 2's gauge without a unit slot for one frame (fixed by the gauge guard, STATE part 6d)",
}


def fault_kind(name, prog):
    """The kind of the fault lines kept beside the pictures (the second pass keeps them), or ''."""
    p = ROOT / "local" / "tests" / ("sw-%s-%s-emulog.txt" % (name, prog))
    if not p.exists():
        return ""
    pcs = {int(x, 16) for x in re.findall(r"pc=0x([0-9a-fA-F]+)", p.read_text(encoding="utf-8", errors="replace"))}
    if not pcs:
        return ""
    for kind, group in (("msn", MSN), ("gauge", GAUGE), ("attach", ATT)):
        if pcs <= group:
            return kind
    if pcs & CONT:
        return "continue"
    return "other"


def classify(room, prog):
    if (room, prog) not in rows:
        return ["NOT RUN"], -1, ""
    head, parts, log = rows[(room, prog)]
    res = parts[1]
    m = re.search(r"TLB misses (\d+)", " | ".join(parts))
    tlb = int(m.group(1)) if m else -1
    snaps = re.findall(r"f(\d+) room ([0-9A-F]{4}) btl (\d+) L(\d) P1 (none|noslot|\d+/\d+ a[0-9A-F]+) P2 (none|noslot|\d+/\d+ a[0-9A-F]+) msn (\d) go (\d)", parts[-1])
    exp = "%02X%02X" % (int(room[2:]), WORLD.get(room[:2], 0xFF))
    cls = []
    if "never out of sync" not in res:
        cls.append("DESYNC" if "OUT OF SYNC" in res.upper() else "NO-END")
    kind = fault_kind(head[3], prog) if tlb > 0 else ""
    if tlb > 0:
        cls.append("OK-GAME" if kind in GAME_KINDS else "FAULT")
    if not snaps:
        cls.append("NO-PROBE")
    else:
        if all(s[1] != exp for s in snaps):
            cls.append("WRONG-ROOM")
        here = [s for s in snaps if s[1] == exp]
        p1 = any(s[4] not in ("none", "noslot") for s in here)
        p2 = any(s[5] not in ("none", "noslot") for s in here)
        if here and not p1:
            cls.append("NO-HERO")
        elif here and not p2:
            cls.append("P2-NONE")
    if "OK-GAME" in cls and len(cls) > 1:
        cls.remove("OK-GAME")
        cls.append("FAULT")
    short = "; ".join("f%s: %s" % (s[0], ("%s / %s%s" % (s[4].split()[0], s[5].split()[0], ", two views" if s[3] == "2" else "")) if s[1] == exp
                      else ("the New Game room (after a Continue)" if s[1] == "0102" else "room %s" % s[1])) for s in snaps)
    if kind:
        short += " [fault lines: %s]" % KIND_WORDS.get(kind, kind)
    return (cls or ["OK"]), tlb, short


progs = collections.defaultdict(list)          # mission name -> [(room, world, prog, party)]
for line in (SW / "missions.txt").read_text(encoding="utf-8").splitlines():
    h = line.split()
    if len(h) >= 5:
        progs[h[3]].append((h[0], h[1], h[2], h[4]))

cup_other = collections.Counter()               # cup mission name -> blocks of it that were not run
cups = SW / "missions-cups.txt"
if cups.exists():
    for line in cups.read_text(encoding="utf-8").splitlines():
        h = line.split()
        if len(h) >= 5:
            if (h[0], h[2]) in rows:
                progs[h[3]].append((h[0], h[1], h[2], h[4]))
            else:
                cup_other[h[3]] += 1

out = ["# The mission sweep: every mission program of the game once, with two heroes",
       "",
       "Made by `python -I tools\\own\\sweep_doc.py` from the logs in `local\\sweep`. Method and limits: `docs\\STATE.md`,",
       "seventh round, part 7b. Story order and row names are those of `docs\\PARITY-CHECKLIST.md`.",
       "",
       "How to read a line: `f5200: 17/20 / 15/20, two views` = at session frame 5200 player 1's hero has 17 of 20 HP,",
       "player 2's hero 15 of 20, and each PC shows its own view. `none` = that player has no hero at that moment.",
       "Every run: two linked emulators, 9,000 frames, level 1 heroes with 20 HP, player 1 presses Circle now and then,",
       "player 2 presses Circle all the time. A run proves that the mission STARTS and RUNS with two heroes in sync;",
       "it does not play a mission to its end.",
       ""]
total = collections.Counter()
body = []
seen = set()
world = None
for line in (DOCS / "PARITY-CHECKLIST.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"### (\d+\. .*)", line)
    if m:
        world = m.group(1)
        continue
    m = re.match(r"- ([A-Z0-9]+-\d+) `([A-Z0-9_]+)`: (.*)", line)
    if not m or world is None:
        continue
    rowid, name, text = m.groups()
    if name not in progs or name in seen:
        continue
    seen.add(name)
    if not body or body[-1][0] != world:
        body.append((world, []))
    for room, w, prog, party in progs[name]:
        cls, tlb, short = classify(room, prog)
        note = ""
        if (room, prog) in notes:
            c, note = notes[(room, prog)]
            if c:
                cls = [c]
        for c in cls:
            total[c] += 1
        body[-1][1].append("| %s | `%s` | %s %s | %s | %s | %s | %s |" % (
            rowid, name, room, prog, " + ".join(cls), "" if tlb < 0 else str(tlb), short, note))
nameless = []
for line in (DOCS / "PARITY-CHECKLIST.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"- ([A-Z0-9]+-\d+) `([A-Z0-9_]+)`: ", line)
    if m and m.group(2) not in progs and (m.group(1), m.group(2)) not in nameless:
        nameless.append((m.group(1), m.group(2)))
rest = [n for n in progs if n not in seen]
if rest:
    body.append(("Missions that are not in the checklist's lists", []))
    for name in sorted(rest):
        for room, w, prog, party in progs[name]:
            cls, tlb, short = classify(room, prog)
            note = ""
            if (room, prog) in notes:
                c, note = notes[(room, prog)]
                if c:
                    cls = [c]
            for c in cls:
                total[c] += 1
            body[-1][1].append("| - | `%s` | %s %s | %s | %s | %s | %s |" % (name, room, prog, " + ".join(cls), "" if tlb < 0 else str(tlb), short, note))
out.append("## Totals (%d mission programs and cup blocks with a result or in the first list)" % sum(len(v) for v in progs.values()))
out.append("")
out.append("| Class | Programs | Meaning |")
out.append("|---|---|---|")
for c, n in sorted(total.items(), key=lambda kv: -kv[1]):
    out.append("| %s | %d | %s |" % (c, n, WORDS.get(c, "")))
out.append("")
for world, lines in body:
    out.append("## " + world)
    out.append("")
    out.append("| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |")
    out.append("|---|---|---|---|---|---|---|")
    out += lines
    out.append("")
if cup_other:
    out.append("## The Olympus cups: blocks that were not run")
    out.append("")
    out.append("A cup round is an \"If Entrance N\" block inside a battle program of the arena room he09 (130 blocks, 44 mission")
    out.append("names). One block of each name was run (the lines of rows HEC-01 to HEC-08 above). Not run, same name and rules:")
    out.append("")
    out.append(", ".join("`%s` %d more" % kv for kv in sorted(cup_other.items())))
    out.append("")
if nameless:
    out.append("## Mission names of the checklist that no room program starts")
    out.append("")
    out.append("These names are in the game's mission files, but no program of any room names them (not in the un-indented")
    out.append("Mission lines and not in the cup blocks). A jump test cannot start them; they were NOT run.")
    out.append("")
    out.append(", ".join("%s `%s`" % kv for kv in nameless))
    out.append("")
(DOCS / "PARITY-SWEEP.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("written: docs/PARITY-SWEEP.md, %d lines; %s" % (len(out), dict(total)))
