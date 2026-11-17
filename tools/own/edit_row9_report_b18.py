"""One-off: tools/own/row9_report.py after test build 18 (eighth round, parts 79 to 83): what the other fights'
forced moves are (holds of one hero), what was run on purpose with two heroes (ten boss rooms), the fault found
at the Groundshaker and its cure (glue 60). Run once, then make the report again; the Xigbar and Luxord texts
are taken from the report as it stands:
  python -I tools/own/edit_row9_report_b18.py
  python -I tools/own/row9_report.py --xig=<file> --lux=<file>     (this script prints the two file names)"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
p = HERE / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "PLAYED ON PURPOSE WITH TWO HEROES" in s:
    raise SystemExit("already there")

# 1. the notes of the fights
RUNS = ("ten boss rooms, both players Circle / Triangle / R1, HP held, 20,000 frames each, candidates v89 and v93; "
        "STATE parts 80 to 83")


def note(state, text):
    return '("%s", "%s")' % (state, text.replace('"', '\\"'))


NEW = {
    "B_BB110": note("OK", "The Dark Thorn. READ: its forced move is a GRAB (the boss attaches the hero to his hand, carries "
                          "and throws him). PLAYED ON PURPOSE WITH TWO HEROES (" + RUNS + "): the boss took player 1's hero 7 "
                          "or 8 times and player 2's 3 times in a run, every hold ended (the longest 620 frames), the other "
                          "hero stayed free; in sync, 0 fault lines."),
    "B_HE020": note("OK", "Cerberus. READ: a GRAB (the bite: the hero is attached to the boss). Played on purpose with two "
                          "heroes (the same runs): player 1's hero 4 times, player 2's once (up to 830 frames), every hold "
                          "ended; in sync, 0 fault lines."),
    "B_LK110": note("OK", "Scar. READ: a GRAB (the hero is attached to the boss). Played on purpose with two heroes (the same "
                          "runs): both heroes were taken (up to 854 frames), every hold ended; in sync, 0 fault lines. Seen "
                          "in the timelines: steps of one hold can land on the two heroes in turn; here both ended."),
    "B_EX130": note("OK", "Xaldin. READ: a blow-away of the hero who was hit (he falls until he lands). Played on purpose "
                          "with two heroes (the same runs): player 1's hero 5 or 6 times, player 2's once (up to 640 "
                          "frames), every one ended; in sync, 0 fault lines. (Before: ran for King Mickey's rescue, "
                          "register G4.)"),
    "B_EX120": note("OK", "Demyx in the Underworld. Played on purpose with two heroes (the same runs): player 1's hero 6 "
                          "times (up to 936 frames), player 2's never in these runs; every hold ended; in sync, 0 fault "
                          "lines."),
    "B_EX120_HB": note("OK", "Demyx in Hollow Bastion. Played on purpose with two heroes (the same runs): player 1's hero "
                             "13 or 14 times, player 2's 4 times (up to 460 frames), every hold ended; in sync, 0 fault "
                             "lines."),
    "B_HE100": note("OK", "The Hydra. Played on purpose with two heroes (the same runs): player 1's hero 9 times, player "
                          "2's twice (up to 140 frames; one move takes both heroes one after the other), every hold "
                          "ended; in sync, 0 fault lines. THE FIFTY-NINTH GLUE (a try: send a boss's capture to the hero "
                          "it already holds) MADE THIS FIGHT WORSE (a hero captured every 60 frames to the end of the "
                          "run); no build uses that glue. (Before: ran with two Drive Forms and two King Mickeys, runs "
                          "mkH2, hyf2.)"),
    "B_LK120": note("FIXED", "The Groundshaker. READ: its forced moves are RIDES (the hero is attached to the boss). FAULT OF "
                             "BUILDS 12 TO 17, found by playing it on purpose with two heroes: while the boss held player "
                             "2's hero, one step of the hold landed on player 1's hero, who was free; nobody ever ended "
                             "it, and he stood frozen (action FE) for the last 11,250 frames of the run. BUILD 18 (glue "
                             "60): a hero in one and the same captured motion for 1,800 steps (a minute) is let go. Shown "
                             "with a stray capture made on purpose (runs orA / orB): without the glue he stays frozen, "
                             "with it he is free again and rides and fights on. In the run of build 18's candidate the "
                             "fault did not come by itself (every hold ended, the longest 1,060 frames)."),
    "B_EX170_LAST": note("OK", "The last Xemnas. Played on purpose with two heroes (the same runs): short holds of both "
                               "heroes (up to 218 frames), every one ended; in sync, 0 fault lines. NOT MET in these runs: "
                               "the part where Xemnas holds Sora and Riku must free him, and the laser part at the end."),
    "B_EX390": note("OK", "The armoured Xemnas. Played on purpose with two heroes (the same runs): player 1's hero 4 or 5 "
                          "times, player 2's 6 times (up to 298 frames), every hold ended; in sync, 0 fault lines."),
}
for k in ("B_HE100", "B_EX130"):
    m = re.search(r'    "%s": \("RUN", ".*?"\),\n' % k, s, re.S)
    assert m, k
    s = s[:m.start()] + s[m.end():]
tail = '''    "B_EX150_LV99": ("RUN", "Data Luxord (run luxd, candidate of build 13): both heroes fight all the time, in sync, "
                            "0 fault lines. His card trick was not met in that run."),
}
'''
assert s.count(tail) == 1
add = "".join('    "%s": %s,\n' % (k, v) for k, v in NEW.items())
s = s.replace(tail, tail[:-2] + add + "}\n")

# 2. section 3: what is open
a = s.index("WHAT IS STILL OPEN: every other boss.")
b = s.index("A FIRST SORTING OF THE OTHER FIGHTS")
s = s[:a] + '''THE OTHER FIGHTS (test build 18; STATE parts 79 to 83). The forced moves of the other bosses were READ in their
scripts and then PLAYED ON PURPOSE WITH TWO HEROES in ten boss rooms (the Dark Thorn, Cerberus, Scar, Xaldin,
Demyx twice, the Hydra, the Groundshaker, the last Xemnas, the armoured Xemnas; both players pressing, HP held,
20,000 frames each):
- What these bosses force on a hero is a HOLD OF ONE HERO BY THE BOSS'S BODY: a grab (the hero is attached to a
  hand or a mouth), a ride, a throw, a blow-away. It is not a face-to-face struggle like Shan-Yu's clash. The
  boss takes either hero; the other one stays free and fights. VERIFIED in the ten rooms: every hold ended.
- "Both heroes inside the same hold" is NOT built for these fights. It would put two heroes into one hand, and
  the hero who is not held is the one who is playing. THAT IS MY READING, NOT A PROOF THAT TWO IS IMPOSSIBLE:
  whether these holds may stay one hero's is the user's decision (`REQUIREMENT-full-parity.md`).
- A FAULT WAS FOUND AND CURED at the Groundshaker (a hero held for ever; glue 60, see its line in the table).
- Not played on purpose: the fights of the other scripts in the sorting below, the last Xemnas's "Riku frees
  Sora" part and his laser part.

'''.replace("\\", "\\\\") + s[b:]

# 3. the legend and the open list
old = ("FIXED = a fault of builds 12 and 13 that build 14 cures, seen in test runs.")
assert s.count(old) == 1
s = s.replace(old, "FIXED = a fault of earlier builds that a later build cures, seen in test runs.")
old = '''- The fights with state RUN or SWEEP: their moves were not played on purpose with two heroes. The rule of part 2
  is the same code for all of them (READ), but only Shan-Yu, the Twilight Thorn, Xigbar and Luxord were VERIFIED.
  A human at the controller will meet the others in a normal play-through; a held hero that never gets free is
  the thing to watch for.
'''
assert s.count(old) == 1
s = s.replace(old, '''- The fights with state RUN or SWEEP: their moves were not played on purpose with two heroes. Since build 18 a
  hero who stays in one and the same held pose for a minute is let go (glue 60), so "a held hero that never
  gets free" should not happen any more; a hero who is let go only after that minute is the thing to tell me.
- The last Xemnas: the part where Xemnas holds Sora and Riku must free him, and the laser part, were not met by
  a test script.
''')
p.write_text(s, encoding="utf-8", newline=chr(10))

# the Xigbar and Luxord texts of the report as it stands, for the generator
rep = (HERE.parent.parent / "docs" / "ROW9-PAIRED-MOVES.md").read_text(encoding="utf-8")
out = HERE.parent.parent / "local" / "sweep" / "b15"
for key, name in (("B_EX140", "row9-xig.txt"), ("B_EX150", "row9-lux.txt")):
    m = re.search(r"^\| `%s` \|.*\| (?:FIXED|OK|RUN) \| (.*) \|$" % key, rep, re.M)
    assert m, key
    (out / name).write_text(m.group(1) + "\n", encoding="utf-8")
    print("the text of", key, "->", out / name)
print("ok")
