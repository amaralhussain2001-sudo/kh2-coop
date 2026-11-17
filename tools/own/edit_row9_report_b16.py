"""One-off: tools/own/row9_report.py after test build 16: section 3 tells what IS built now (both heroes in Shan-Yu's
clash) and what is still open, and Shan-Yu's line in the table gets the new facts. Run once, then make the report
again (python -I tools/own/row9_report.py --xig=... --lux=...).
  python -I tools/own/edit_row9_report_b16.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "BUILT FOR THE FIRST FIGHT" in s:
    raise SystemExit("already there")
a = s.index('## 3. "Both heroes in the same move at once" (the second half of row 9): NOT BUILT YET')
b = s.index("## 4. The fights, one by one")
new = '''## 3. "Both heroes in the same move at once" (the second half of row 9): BUILT FOR THE FIRST FIGHT, Shan-Yu's clash (test build 16)

The user's decision of 2026-11-10 stands: both heroes do a boss's scripted move together; one hero alone is only
the fallback where two is PROVEN impossible, reported per fight. That proof exists for no fight.

WHAT BUILD 16 DOES, at Shan-Yu's gate (VERIFIED, runs tg35 to tg39 of candidate v74; STATE parts 61 to 66):
- When Shan-Yu's script hooks its clash onto one hero and the other hero is up, free and within 500 units, the
  other hero is put beside and a little behind the first and is in the clash too.
- Each player has "Press" (and "Takedown") in his own menu, and each player's Triangle pushes. One press makes
  both heroes push and counts once.
- The clash's clock runs as in the game (one script steps the boss's numbers).
- A hero who is far away stays free. A grab, or the falcon's lift, stays the grabbed hero's alone.

HOW (READ, then built): the hero's side of a boss's move is a script that the boss's script HOOKS onto the hero
(`trap_obj_hook`). The second hero gets his own copy of that hooked script. My three "reasons of risk" of the
first version of this report did not hold: the second hero plays the move where he is put, not inside the first;
with his own copy of the script his move ends by itself; and a hero who wants to stay free only has to stand
away.

WHAT IS STILL OPEN: every other boss. 43 of the 99 boss scripts hook a script onto the hero. For each fight it
must be read whether the move is FORCED on the hero (then "together" fits) or is the answer to the hero's own
command (then it stays that hero's), which of the boss's numbers the hero-side script steps (they must be
stepped once), and it must be run. The fiftieth glue has the room as its one switch; today that is world 08,
room 09.

A FIRST SORTING OF THE OTHER FIGHTS (READ in the decoded scripts with `tools\\own\\row9_hooks.py`; it follows the
scripts' own calls from the REACTION_CALLBACK, so a hook that an act started by a command makes is counted as
"not an answer"; each line needs a human look before it is built):
- 17 of the 43 scripts have at least one hook that is NOT the direct answer to a hero's command (a move the boss
  may FORCE): B_MU100 Shan-Yu (1: the clash, BUILT); B_BB110 the Dark Thorn (1); B_CA040 / B_CA040_PUB the Grim
  Reaper (1); B_EX100 the Twilight Thorn (2, beside 7 answers); B_EX120 / _HB / _HB_LV99 (1); B_EX130 / _LV99
  Xaldin (1); B_EX170_LAST / _LV99 the last Xemnas (7, beside 10 answers); B_EX390 (1, in its start-up);
  B_HE020 Cerberus (1); B_HE100 the Hydra (1, beside 4 answers); B_LK110 Scar (1); B_LK120 the Groundshaker (3).
- In the other 26 scripts every hook is the answer to the hero's own command: there the move is that hero's
  own, and "one hero does it" is what the command means (builds 13 and 14).

'''
s = s[:a] + new + s[b:]
old = '''    "B_MU100": ("OK", "Shan-Yu. VERIFIED (runs gp11, gp13, gp14, gp12, cap6, cap7; STATE parts 32, 33, 38): his clash "
                      "takes the hero he holds, the green \\"Press\\" is in THAT hero's menu, that player's presses "
                      "count, player 2 alone wins the fight. With BOTH players pressing, 5 clashes of 6 keep one hero; "
                      "one had 4 stray calls for the other hero (cause not found)."),'''
assert s.count(old) == 1, s.count(old)
new2 = '''    "B_MU100": ("OK", "Shan-Yu. SINCE BUILD 16 BOTH HEROES ARE IN HIS CLASH when the second stands within 500 units: "
                      "each has \\"Press\\" in his own menu, each one's Triangle pushes, the clash's clock is the game's "
                      "(VERIFIED, runs tg35 to tg39; STATE parts 61 to 66). A hero far away stays free; then the clash "
                      "takes the one hero, as in builds 13 to 15 (runs gp11 to gp14, cap6, cap7; STATE parts 32, 33, 38)."),'''
s = s.replace(old, new2)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
