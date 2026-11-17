"""One-off: KH2-COOP-PLAN.md after test build 15 (eighth round, plan row 39 stage 1a): a second status sentence
at the end of row 39 and a new row 48. Run once:  python -I tools/merge/add_plan_rows_v8.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 48 |" in t:
    raise SystemExit("already there")
lines = t.split("\n")
done = False
for i, l in enumerate(lines):
    if l.startswith("| 39 |"):
        assert l.rstrip().endswith("|")
        lines[i] = l.rstrip()[:-1].rstrip() + (
            " **STATUS 2026-11-14, later (test build 15): STAGE 1a IS BUILT AND VERIFIED: player 2's own ARMOUR AND "
            "ACCESSORIES.** He chooses them in the pause menu when HE opened it; the bag is common. His eight places "
            "live inside Sora's own record, in the places 5 to 8 that the hero never has (a test showed that they do "
            "nothing for the hero), so they are saved with the game's own save and no new place in the save file "
            "was needed. STILL OPEN under this row: own Keyblade (the weapon's model and files), own abilities "
            "(it is not known whether the game keeps the ability list in a fixed order), own item places, own "
            "bag and wallet, \"everything given goes to each\". (docs\\STATE.md, Eighth round, parts 52 to 58.) |")
        done = True
assert done
last = max(i for i, l in enumerate(lines) if l.startswith("| 47 |"))
row48 = ("| 48 | TEST BUILD 15 (eighth round, 2026-11-14) | Build 14 + two glues (48, 49; `tools\\merge\\merge_v7.py "
         "--ownrec --ownmenu`): the second hero's unit slot reads a view of the hero's record with player 2's "
         "armour and accessory places; while player 2's pause menu is open his places and the hero's change "
         "places in that record. Plan row 39, stage 1a. The disc file is still the one of build 12. Details and "
         "evidence: docs\\STATE.md, section \"Eighth round\", parts 52 to 58. |")
lines.insert(last + 1, row48)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: row 39 has its stage 1a status, row 48 is added")
