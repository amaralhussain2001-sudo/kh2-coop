"""One-off: KH2-COOP-PLAN.md after test build 16 (eighth round): a status sentence at the end of rows 9, 35 and
36, and a new row 49. Run once:  python -I tools/merge/add_plan_rows_v9.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 49 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 9 |": (
        " **STATUS 2026-11-14, later (test build 16): THE SECOND HALF IS BUILT AND VERIFIED FOR THE FIRST FIGHT, "
        "SHAN-YU'S CLASH.** When the boss's script hooks its clash onto one hero and the other hero is up, free "
        "and within 500 units, the other hero is put beside him, gets his own copy of the hooked script, has "
        "\"Press\" and \"Takedown\" in his own menu, and his own Triangle pushes; one press makes both heroes push "
        "and counts once; the clash's clock runs as in the game; a hero far away stays free; a grab or the "
        "falcon's lift stays one hero's. STILL OPEN under this row: every other boss with a forced, hooked move "
        "(43 of the 99 boss scripts hook a script onto the hero; each fight needs its room in the glue's "
        "switch, its numbers to keep, and its own runs). No fight has been PROVEN impossible. "
        "(docs\\STATE.md, Eighth round, parts 61 to 66.) |"),
    "| 35 |": (
        " **STATUS 2026-11-14 (test build 16): PLAYER 2'S SHIP CAN BE HIT AND HAS ITS OWN HULL** (fifty-first glue: "
        "every shot's question \"does this touch the player ship\" is also asked for ship 2). The mission is over "
        "when EITHER ship falls (the Light Cycle rule of row 36); the one hull gauge shows the weaker ship; a "
        "repair mends both. Still one score, one gauge with no mark for whose ship it shows, one lock-on. "
        "(docs\\STATE.md, Eighth round, parts 67 and 69.) |"),
    "| 36 |": (
        " **STATUS 2026-11-14 (test build 16): A CARPET UNDER EACH HERO** (fifty-second glue: a second carpet is "
        "made with the game's own routine when both heroes are carpet riders; its state routine follows player "
        "2's hero; no new disc). The toy cannon, the sidecar and the carpet escape are still one hero for both "
        "(row 37): NOT built, and not proven impossible; what is known is in docs\\STATE.md, Eighth round, part "
        "67 and the parts after it. |"),
}
lines = t.split("\n")
done = set()
for i, l in enumerate(lines):
    for k, text in ADD.items():
        if l.startswith(k):
            assert l.rstrip().endswith("|") and k not in done
            lines[i] = l.rstrip()[:-1].rstrip() + text
            done.add(k)
assert done == set(ADD), done
last = max(i for i, l in enumerate(lines) if l.startswith("| 48 |"))
row49 = ("| 49 | TEST BUILD 16 (eighth round, 2026-11-14) | Build 15 + three glues (50, 51, 52; `tools\\merge\\merge_v7.py "
         "--ownrec --ownmenu --together --ship2hit --carpet2`): both heroes in Shan-Yu's clash (plan row 9, second "
         "half, first fight); player 2's Gummi ship can be hit and has its own hull (row 35); a carpet under each "
         "hero (row 36). The disc file is still the one of build 12. Details and evidence: docs\\STATE.md, section "
         "\"Eighth round\", parts 61 to 70. |")
lines.insert(last + 1, row49)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: rows 9, 35 and 36 have their build 16 status, row 49 is added")
