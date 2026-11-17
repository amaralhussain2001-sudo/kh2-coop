"""One-off, AFTER edit_package_v13.py: the read-me's older lines that build 13 makes wrong, and the known problems
of build 13 (eighth round). It edits only tools/package/kit/1-READ-ME-FIRST (KH2 TEST).txt.
  python -I tools/package/edit_readme_v13.py          (run ONCE; it refuses a second run)
"""
import pathlib

README = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = README.read_text(encoding="utf-8")
if "TEST BUILD 13" not in t:
    raise SystemExit("run edit_package_v13.py first")
if "BUILD 13, KNOWN AND NOT SOLVED" in t:
    raise SystemExit("already done")
PAIRS = [
    ("""  a door. ONE form at a time: while one hero is in a form the other's Drive row is dim (the game's own rule; a
  form uses up Donald or Goofy). Tested for player 2 with Limit, Valor, Wisdom, Master and Final Form (the
""", """  a door. SINCE BUILD 13 BOTH HEROES CAN BE IN A FORM AT THE SAME TIME (tested: Valor with Wisdom, Limit Form
  with Limit Form, Limit Form with Final). A form's row is dim for you only when the helper it needs is away
  (the other hero's form is using Donald or Goofy: the game's own rule), or when the room has no memory left
  for a second form (seen in the Hydra's room). When one hero leaves his form, only the helpers that no form
  still uses come back. Tested for player 2 with Limit, Valor, Wisdom, Master and Final Form (the
"""),
    ("""- A boss move that grabs or carries a hero takes ONE hero. Its opening moves always took player 1's hero in the
  first big boss fight of the Roxas part; later moves take whoever the boss reaches.
""", """- A boss move that grabs or carries a hero takes ONE hero. Its opening moves always took player 1's hero in the
  first big boss fight of the Roxas part; later moves take whoever the boss reaches.
  SINCE BUILD 13 the move's green command is in the menu of the player whose hero is in the move, and HIS
  buttons count (tested at Shan-Yu's gate clash: player 2 alone can win it). The other hero stays free and
  can go on fighting. Two heroes inside the same move at once is not built.
- BUILD 13, KNOWN AND NOT SOLVED: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK (both in The World That Never
  Was) do not work right with two heroes: a hero can stay held for the rest of the fight. It was so in build
  12 too (there Xigbar's fight could even stop the game). SAVE BEFORE these two fights and tell me what you saw.
- KING MICKEY (when both heroes fall in a fight where the King can come): since build 13 EACH player plays a
  King Mickey. The two share one HP bar and one Drive gauge. Healing Light brings both heroes back.
- Enemy groups now wake up when EITHER hero walks into their place (before build 13 only for player 1's hero).
- Not met by any test script, so not tested: the Large Body's and the Samurai's green commands for player 2.
"""),
]
for old, new in PAIRS:
    assert t.count(old) == 1, old[:60]
    t = t.replace(old, new)
README.write_text(t, encoding="utf-8")
print("read-me edited for build 13")
