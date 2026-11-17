"""One-off: tools/own/row9_report.py after the ninth round (test build 20; STATE parts 93 to 100): both heroes inside
the same hold of a boss (glue 65), the Groundshaker's cause, Luxord's trick (glue 67), the last Xemnas's later
parts and who steers Riku (glue 68), and THE 40 "RUN / SWEEP" FIGHTS AND THE TEN BOSS ROOMS PLAYED ON PURPOSE on build 20's candidate (their numbers
come from tools/own/row9_rs2.py when the report is made). Run once, then make the report again:
  python -I tools/own/edit_row9_report_b20.py
  python -I tools/own/row9_report.py --xig=local/sweep/b15/row9-xig.txt --lux=local/sweep/b15/row9-lux.txt"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
p = HERE / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "row9_rs2.py" in s:
    raise SystemExit("already there")


def note(state, text):
    return '("%s", "%s")' % (state, text.replace('"', '\\"'))


OWNCMD = ("In the test runs every capture in this fight was the answer to a hero's OWN green command; such a move stays "
          "that hero's own (section 3, \"what is not a pair, and why\").")
NEW = {
    "B_BB110": note("PAIR", "The Dark Thorn. READ: its forced move is a GRAB (the boss attaches the hero to his hand, carries and "
                            "throws him). BUILD 20: BOTH HEROES INSIDE THE SAME GRAB. Seen on candidate v107 (run h7, STATE part "
                            "97): 2 pairs of 182 frames, both heroes thrown off together. An earlier form of the glue left a "
                            "hero frozen here for 7,806 frames (part 96): its \"let him go\" did not work; the one that works "
                            "was found by trying 14 ways. The answers to a hero's own command (\"Catch\" and what follows) stay "
                            "that hero's."),
    "B_HE020": note("PAIR", "Cerberus. READ: a GRAB (the bite: the hero is attached to the boss). BUILD 20: BOTH HEROES INSIDE THE "
                            "SAME BITE. Seen: candidate v104 (run h4, part 95): a pair from frame 7180 to 7658, the moves FD, FE, "
                            "FF on both heroes in the same frames, both free within two frames; candidate v107 (run h7): 2 "
                            "pairs."),
    "B_LK110": note("PAIR", "Scar. READ: a GRAB (the hero is attached to the boss). BUILD 20: BOTH HEROES INSIDE THE SAME GRAB. "
                            "Seen: candidate v104 (run h4): a pair of 506 frames, the moves FC, FD, FE on both, both free in the "
                            "same frame; candidate v107 (run h7): 2 pairs."),
    "B_EX130": note("OWN", "Xaldin. READ: a blow-away of the hero who was hit, and the hero's own jumps (\"Learn\" / \"Jump\"). "
                           + OWNCMD + " Every hold ended."),
    "B_EX120": note("OWN", "Demyx in the Underworld (the water forms: the hero takes a form by his own command). " + OWNCMD
                           + " Every hold ended (the longest in one action 792 frames, run h7)."),
    "B_EX120_HB": note("OWN", "Demyx in Hollow Bastion (the same moves as B_EX120). " + OWNCMD + " Every hold ended."),
    "B_HE100": note("PAIR", "The Hydra. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD. Seen on candidate v104 (run h4, part 95): three "
                            "pairs of 94 frames (move FD on both heroes). THE FIFTY-NINTH GLUE (a try of build 18: send a "
                            "boss's capture to the hero it already holds) made this fight worse; no build uses it."),
    "B_LK120": note("FIXED", "The Groundshaker. READ: its forced moves are RIDES (the hero is attached to the boss). THE FAULT OF "
                             "BUILDS 12 TO 17 (a hero frozen for the rest of the fight) HAS ITS REAL CAUSE NOW (part 94): the "
                             "script's attack-hit routine (OBJ_ATTACK -> L4217) captures, with move 254, whichever hero its "
                             "attack HITS while the ride flag is set: also the hero who stands beside the ride, and nothing "
                             "ever ends that capture. BUILD 20: a stray capture of a free bystander is not made (shown on a "
                             "state made on purpose, run gsI: the hero stays free and joins the ride 42 frames later). BOTH "
                             "HEROES RIDE TOGETHER (run h7: one pair of 996 frames). The nets stay (build 18's one-minute "
                             "rule; the mirror's 40 steps), both shown on made states (runs gsG, gsH)."),
    "B_EX170_LAST": note("PAIR", "The last Xemnas. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD in his opening move (move 0x101, runs "
                                 "h4 / h7), in THE PART WHERE RIKU MUST FREE SORA (run xeB, part 97: both Xemnas objects' HP "
                                 "written to 150 at frame 6500; the part runs from frame 10006 to 13434, both heroes held, the "
                                 "fight goes on) and in THE LASER PART AT THE END (runs xeC / xeD: HP 40 / 1; move 0x106 on both "
                                 "heroes and on Riku from frame 7690, both stand in the dome, the \"Reflect\" commands; the "
                                 "fight ends). WHO STEERS RIKU (part 100): the boss's script gives Riku to the player whose hero it named "
                                 "(runs xeG / xeH / xeI on v112: only that player's stick moved him). BUILD 20 (glue 68): while "
                                 "both heroes are held both controllers count, so BOTH PLAYERS STEER RIKU (run xeN on v115: "
                                 "player 1's stick alone moves him; xeO: player 2's; xeP: both mash, the part plays and the "
                                 "fight goes on)."),
    "B_EX390": note("PAIR", "The armoured Xemnas. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD (the moves 0x100 and FD). Seen: "
                            "candidate v104 (run h4): four pairs; candidate v107 (run h7): 10 pairs, every one ended for "
                            "both."),
    "B_EX150": note("FIXED", "@LUX@ BUILD 20 (glue 67): see B_EX150_LV99; the story fight on candidate v113 (run lxR): player 1's "
                             "hero held 11 times, player 2's 7 times, the longest hold in one action 114 frames."),
    "B_EX150_LV99": note("FIXED", "Data Luxord. FAULT OF BUILDS 14 TO 19, found in the ninth round: a hero who lost a card or command "
                                  "trick stood in the captured move 254 for up to a minute (3,602 frames, run lxI; ended only by "
                                  "the one-minute rule). THE CAUSE (READ, then shown by a control, part 99): the act of Luxord "
                                  "that turns the loser into the card or the die, and so lets him go, waits 100 steps first; "
                                  "the OTHER hero's hit in that time started Luxord's damage act, which replaced it. With the "
                                  "other player not pressing the hold ends by itself (run lxQ: 130 frames). BUILD 20 (glue 67): "
                                  "while a hero stands in Luxord's trick, a hit takes HP but is no \"reaction\". Run lxP: "
                                  "player 1's hero lost five tricks (336, 126, 130, 130, 392 frames), player 2's three (128, "
                                  "130, 130); every one ended by the script."),
}
for k, v in NEW.items():
    m = re.search(r'    "%s": \("[A-Z ]+", .*?\),\n' % k, s, re.S)
    assert m, k
    s = s[:m.start()] + '    "%s": %s,\n' % (k, v) + s[m.end():]

# section 3: the other fights
a = s.index("THE OTHER FIGHTS (test build 18; STATE parts 79 to 83).")
b = s.index("A FIRST SORTING OF THE OTHER FIGHTS")
s = s[:a] + '''THE OTHER FIGHTS (test build 20; STATE, "Ninth round", parts 93 to 100). The user's word of 2026-11-15: "a boss's
hold takes one hero" is an exception he gave no OK for: build "both heroes inside the same hold", or prove per
boss why it cannot be done.
BUILT (glue 65, `merge_v7.py --holdpair`; VERIFIED in the runs of the table):
- When an enemy's script captures a hero or attaches him to itself, and that is NOT the answer to this hero's own
  green command, the other hero (up, not held by another captor) is put into the same hold, wherever he stands:
  every call of the captor's script for the first hero (capture, attach, detach, place, direction, flags, the
  motion calls, "blow") is made for the second too. One script drives the hold; both are let go together.
- A hero who is down is not taken. Shan-Yu's room keeps its own rule (build 16).
- THE NETS: a mirror hero left behind is thrown off 40 steps after the named hero is free (or after 1,200 frames
  without a call that names him); a hero in one and the same captured motion for a minute is thrown off (glue 60
  of build 18). "Thrown off" = detach, "motion start 16", "blow" without speed: the one way of 14 tried that frees
  a hero (part 96).
- THE GROUNDSHAKER'S REAL CAUSE is found and cured, and LUXORD'S TRICKS let the loser go in time (glue 67): see
  their lines in the table.
WHAT IS NOT A PAIR, AND WHY (the per-boss reason asked for):
- A MOVE THAT A HERO STARTS WITH HIS OWN GREEN COMMAND (Xaldin's jumps, Demyx's water forms, Xigbar's sniper answer,
  Luxord's games, and the answers in the scripts of the sorting below). READ: such a move is an ACT OF THE BOSS:
  an object runs one act at a time, the act plays the boss's half of the paired motion and keeps ONE record of
  its partner in the script's work memory, and it is steered by the commands of the hero who pressed. So two
  heroes cannot each have their OWN copy of the move (VERIFIED the hard way in build 13: with two partners
  Xigbar's sniper part never ended and Luxord's trick held a hero for the whole fight; build 14 cured both by
  "the first press takes the command"). A second hero inside the SAME copy could only be a mirror without any
  input, for as long as the first player goes on pressing (Luxord's command game: 20 seconds; Xigbar's sniper
  part: to its end): a passenger, which `REQUIREMENT-full-parity.md` forbids. Outside the move he keeps playing,
  and the command is in his own menu as soon as the boss is free again. THIS IS MY RECOMMENDED OPTION, TAKEN AND
  NOTED; IT IS AN EXCEPTION IN THE USER'S SENSE AND WAITS FOR HIS OK (asked in the final report of the round).
- The mirror hero of a pair has no hooked script of his own (the boss's script hooks one piece onto one hero);
  where that piece reads a controller, it reads the named hero's. BUILD 20 (glue 68, `merge_v7.py --holdpads`):
  WHILE BOTH HEROES OF A PAIR ARE HELD, BOTH CONTROLLERS COUNT (the buttons of either, without START, and the
  moving stick), so both players press in a hold, and in the last Xemnas's "Riku frees Sora" part both
  players steer Riku (part 100).

'''.replace("\\", "\\\\") + s[b:]

# the legend
old = "FIXED = a fault of earlier builds that a later build cures, seen in test runs."
assert s.count(old) == 1
s = s.replace(old, old + '''
PAIR = build 20 puts both heroes inside the same hold; seen in test runs. OWN = in the test runs every capture was
the answer to a hero's own command (his own move, section 3). PLAYED = played on purpose with two heroes on
build 20's candidate (20,000 frames, both players Circle / Triangle / R1, HP held, the capture log): every hold
ended, in sync.''')

# what is still open
a = s.index("- The fights with state RUN or SWEEP: their moves were not played on purpose with two heroes.")
b = s.index("- The Large Body's command and the Samurai duel")
s = s[:a] + '''- The moves that a hero starts with his own command stay that hero's own (section 3): my recommended option,
  it waits for the user's OK.
- How it feels when both players steer the one Riku (the last Xemnas's hold) is for the user's test.
- The pairs were made by test scripts that press Circle, Triangle and R1 blindly. How a pair looks and feels
  (two heroes in one hand) is for the user's test.
''' + s[b:]

# the generator: the fights played on purpose on build 20's candidate
old = '''    lines = []
    count = {}
    for t in table:
        state, text = NOTES.get(t["script"], ("", ""))
        text = text.replace("@XIG@", xig).replace("@LUX@", lux)
'''
assert s.count(old) == 1
s = s.replace(old, '''    played = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "own" / "row9_rs2.py"), "--json"],
                                       capture_output=True, text=True, check=True).stdout)
    by_room = {}
    for o in played:
        by_room.setdefault(o["room"], []).append(o)
    lines = []
    count = {}
    for t in table:
        state, text = NOTES.get(t["script"], ("", ""))
        text = text.replace("@XIG@", xig).replace("@LUX@", lux)
        mine = [o for r in t["rooms"] for o in by_room.get(r, [])]
        if mine:
            parts = []
            for o in mine:
                one = "%s %d: %s, %d fault lines, player 1's hero held %d times, player 2's %d times" % (
                    o["room"], o["program"], "in sync" if o["sync"] else "NOT IN SYNC", o["tlb"], o["p1"][0], o["p2"][0])
                if o["p1"][0] or o["p2"][0]:
                    one += " (the longest hold in one action %d frames)" % max(o["p1"][2], o["p2"][2])
                if o["pairs"]:
                    one += ", BOTH HEROES INSIDE THE SAME HOLD %d times (the longest %d frames)" % (o["pairs"], o["pair_longest"])
                parts.append(one)
            text = (text + " " if text else "") + "ON BUILD 20's CANDIDATE, PLAYED ON PURPOSE WITH TWO HEROES: " + "; ".join(parts) + "."
            if state in ("", "RUN", "SWEEP"):
                state = "PAIR" if any(o["pairs"] for o in mine) else "PLAYED"
''')
old = '''    order = ["OK", "FIXED", "RUN", "OPEN", "SWEEP", "NO ROOM"]'''
assert s.count(old) == 1
s = s.replace(old, '''    order = ["OK", "PAIR", "FIXED", "OWN", "PLAYED", "RUN", "OPEN", "SWEEP", "NO ROOM"]''')
old = '''Written 2026-11-14 for job 10 of the job list ("build it or write the per-fight report"). Made by'''
assert s.count(old) == 1
s = s.replace(old, '''Written 2026-11-14 for job 10 of the job list ("build it or write the per-fight report"); brought up to test build
20 on 2026-11-15 (the ninth round: both heroes inside the same hold). Made by''')
old = '''The evidence behind every line is in `docs\\\\STATE.md`, section "Eighth round".'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, '''The evidence behind every line is in `docs\\\\STATE.md`, sections "Eighth round" and "Ninth round".''')
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
