"""One-off: KH2-COOP-PLAN.md after the eighth round (test build 13): a status sentence at the end of the rows
9, 39 to 45, and a new row 46 that says what build 13 is. Run once:  python -I tools/merge/add_plan_rows_v7.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 46 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 9 |": " **STATUS 2026-11-14 (test build 13): the first half is built.** A boss's paired move takes the hero it "
             "holds or the nearer one, and its green command is in THAT player's menu only; seen in Shan-Yu's clash, "
             "player 2 alone wins it. The same code serves all 52 boss scripts with paired moves; only Shan-Yu and "
             "the Twilight Thorn were looked at. \"Both heroes in the move together\" is NOT built, by decision: "
             "the move has one victim's place, and a second victim would spread the \"held for ever\" fault of "
             "Xigbar and Luxord. **BUILD 14:** a boss's green command is taken by ONE hero: the hero who presses is "
             "\"the player\" of the boss's script for that move, and a boss that holds one hero does not take the "
             "other hero's press. That cures Xigbar's sniper part (it never ended when both pressed) and Luxord's "
             "card trick (a hero stayed held for the whole fight). THE PER-FIGHT REPORT with the reasons: "
             "docs\\ROW9-PAIRED-MOVES.md (evidence: docs\\STATE.md, Eighth round, parts 32, 33, 40, 45 to 50).",
    "| 39 |": " **STATUS 2026-11-14: NOT BUILT.** The feasibility study is written (docs\\STATE.md, Eighth round, part "
              "25): feasible in three stages, the one real risk is the place in the save file.",
    "| 40 |": " **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED.** The game counted both heroes' hits in full "
              "(a real gap); now each hero's hit counts three quarters while there are two heroes.",
    "| 41 |": " **STATUS 2026-11-14: TESTED, NO GAP, NOTHING BUILT.** Player 2 was not hurt once during three Limits.",
    "| 42 |": " **STATUS 2026-11-14: TESTED, NO GAP, NOTHING BUILT.** Both heroes fight their own crowds.",
    "| 43 |": " **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED.** 26 of 100 HP instead of 25.",
    "| 44 |": " **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED** for Valor + Wisdom, Limit + Limit, Limit + "
              "Final, also through a door. A second form is refused when its helper is away or when the game's file "
              "memory has no room (seen in the Hydra's room). When one form ends only its own helpers come back.",
    "| 45 |": " **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED: A KING MICKEY FOR EACH PLAYER** (Shan-Yu, Storm "
              "Rider, the Hydra). The two Mickeys share one HP bar and one Drive gauge; whichever ends the rescue, "
              "both heroes come back. The fallback (one Mickey by a roll) was not needed.",
}
lines = t.split("\n")
done = set()
for i, l in enumerate(lines):
    for key, text in ADD.items():
        if l.startswith(key) and key not in done:
            assert l.rstrip().endswith("|"), key
            lines[i] = l.rstrip()[:-1].rstrip() + text + " |"
            done.add(key)
assert done == set(ADD), sorted(set(ADD) - done)
last = max(i for i, l in enumerate(lines) if l.startswith("| 45 |"))
row46 = ("| 46 | TEST BUILD 13 (eighth round, 2026-11-14) | Build 12 + fourteen new glues (30 to 43, "
         "`tools\\merge\\merge_v7.py`): enemy groups wake up for player 2 too; rows 40, 43, 44, 45 and the first "
         "half of row 9; the Keyblade change in the menu no longer stops the game with two heroes; a form kept "
         "through a door no longer brings back the helpers it uses. The disc file is the same as in build 12. "
         "Details and evidence: docs\\STATE.md, section \"Eighth round\". |")
lines.insert(last + 1, row46)
row47 = ("| 47 | TEST BUILD 14 (eighth round, 2026-11-14) | Build 13 + three glues (44, 45, 47; the same builder with "
         "no option): a boss's Reaction Command is taken by one hero (the sender is the script's player; a boss "
         "that holds one hero does not take the other hero's command); Luxord's card / die takes the hero the "
         "trick is played on. Closes the faults F10 (Xigbar's sniper part) and F11 (Luxord's card trick) of builds "
         "12 and 13. The disc file is still the one of build 12. Details and evidence: docs\\STATE.md, section "
         "\"Eighth round\", parts 45 to 50. |")
lines.insert(last + 2, row47)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan rows updated:", ", ".join(sorted(k.strip("| ") for k in done)), "+ rows 46 and 47")
