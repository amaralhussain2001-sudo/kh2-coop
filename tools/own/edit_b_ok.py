"""One-off (ninth round, STATE part 109): the user's OK of 2026-11-15 evening for "a move started by a hero's own green command stays
that hero's own" goes into docs/REQUIREMENT-full-parity.md (an appended section), the plan's row 9 (a status sentence) and
tools/own/row9_report.py (the OWN state and the open list), then the report is made again by hand:
  python -I tools/own/edit_b_ok.py
  python -I tools/own/row9_report.py --xig=local/sweep/b15/row9-xig.txt --lux=local/sweep/b15/row9-lux.txt"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
WORD = ("\"B OK. Keep player-initiated green Reaction Commands exclusive to the player who activates them. The other player "
        "should remain free to continue fighting.\"")

req = ROOT / "docs" / "REQUIREMENT-full-parity.md"
t = req.read_text(encoding="utf-8")
if "THE USER'S OK OF 2026-11-15" in t:
    raise SystemExit("already there")
t = t.rstrip("\n") + "\n\n" + """## The user's decisions on this requirement (added by the project, not his text above)

- THE USER'S OK OF 2026-11-15 (evening): a move that a hero starts with his OWN green command (a player-initiated Reaction
  Command: Xaldin's jumps, Demyx's water forms, Xigbar's sniper part, Luxord's games and the like) stays that hero's alone,
  and the other hero stays free and keeps fighting. His words: """ + WORD + """
  This is an exception to point 5 above that he approved; it is the behaviour of builds 14 to 21.
- The same message asks for the bosses' AUTOMATIC grabs: "For single-target attacks, prefer capturing only the targeted player.
  For genuinely shared boss mechanics, both players should participate meaningfully." (docs\\STATE.md, Ninth round, part 109
  and the parts after it.)
"""
req.write_text(t, encoding="utf-8", newline="\n")
print("requirement: the OK is written")

plan = ROOT / "KH2-COOP-PLAN.md"
t = plan.read_text(encoding="utf-8")
lines = t.split("\n")
for i, l in enumerate(lines):
    if l.startswith("| 9 |"):
        assert l.rstrip().endswith("|")
        lines[i] = l.rstrip()[:-1].rstrip() + (" **2026-11-15, evening: THE USER'S OK: a move a hero starts with his own green command "
                                               "stays that hero's alone; the other keeps fighting (" + WORD.replace("\"", "'") +
                                               "). His next word on the automatic grabs: a single-target attack takes only the targeted "
                                               "hero, a genuinely shared mechanic both (docs\\STATE.md, part 109 and after).** |")
        break
else:
    raise SystemExit("no row 9")
plan.write_text("\n".join(lines), encoding="utf-8")
print("plan: row 9 has the OK")

rep = ROOT / "tools" / "own" / "row9_report.py"
s = rep.read_text(encoding="utf-8")
pairs = [
    ("""- The moves that a hero starts with his own command stay that hero's own (section 3): my recommended option,
  it waits for the user's OK.
""", """- (Closed 2026-11-15: the moves that a hero starts with his own command stay that hero's own: THE USER'S OK.)
"""),
    ("""  part: to its end): a passenger, which `REQUIREMENT-full-parity.md` forbids. Outside the move he keeps playing,
  and the command is in his own menu as soon as the boss is free again. THIS IS MY RECOMMENDED OPTION, TAKEN AND
  NOTED; IT IS AN EXCEPTION IN THE USER'S SENSE AND WAITS FOR HIS OK (asked in the final report of the round).""",
     """  part: to its end): a passenger, which `REQUIREMENT-full-parity.md` forbids. Outside the move he keeps playing,
  and the command is in his own menu as soon as the boss is free again. THE USER GAVE HIS OK ON 2026-11-15:
  "B OK. Keep player-initiated green Reaction Commands exclusive to the player who activates them. The other
  player should remain free to continue fighting\""""),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep.write_text(s, encoding="utf-8", newline="\n")
print("report source: the OK is in")
