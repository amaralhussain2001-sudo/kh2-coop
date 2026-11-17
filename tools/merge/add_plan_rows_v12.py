"""One-off: KH2-COOP-PLAN.md after test build 20 (ninth round): a status sentence at the end of the rows 9, 35, 36, 37
and 39, and a new row 52. Run once:  python -I tools/merge/add_plan_rows_v12.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 52 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 9 |": (
        " **STATUS 2026-11-15, later (test build 20; the user's word of that day: NO OK for \"a boss's hold takes one "
        "hero\"): BOTH HEROES INSIDE THE SAME HOLD IS BUILT** (glue 65): when a boss's script captures a hero or attaches "
        "him to itself, and that is not the answer to this hero's own green command, the other hero is put into the "
        "same hold, wherever he stands; one script drives the hold for both; both are let go together. Seen at "
        "Cerberus, Scar, the Dark Thorn, the Hydra, the Groundshaker's ride, the armoured Xemnas and the last Xemnas "
        "(his opening, the part where Riku frees Sora, the laser part: both reached by a script), and in the 40 "
        "other fights of the report, played on purpose. While a boss holds both heroes both controllers count (glue "
        "68): both players steer Riku. The Groundshaker's REAL cause is found and cured (its attack-hit routine "
        "captured a bystander); the one-minute rule and a rule for a mirror hero left behind stay as nets, with a "
        "\"let him go\" that works. Luxord's tricks let the loser go in time (glue 67: the other hero's hit broke off "
        "the act that frees him). NOT A PAIR, MY RECOMMENDED OPTION, IT WAITS FOR THE USER'S OK: a move that a hero "
        "starts with his own green command stays that hero's own (the boss has one body and one act, steered by the "
        "presses of the hero who took the command; a second hero inside could only be a passenger). "
        "(docs\\STATE.md, Ninth round, parts 93 to 101; docs\\ROW9-PAIRED-MOVES.md.) |"),
    "| 35 |": (
        " **STATUS 2026-11-15 (test build 20): A SCORE FOR EACH PLAYER** (glue 66): a cannon shot's points go to the ship "
        "that fired it; player 1's number stands in the SCORE frame, player 2's beside it; a digit left of the hull "
        "gauge says whose ship the gauge shows. The points of other weapons than cannons cannot be told apart yet "
        "and go to player 1's number; the mission's result and medals use the sum, as before. (docs\\STATE.md, "
        "Ninth round, part 97.) |"),
    "| 36 |": (
        " **STATUS 2026-11-15 (test build 20): the toy cannon has a view for each player now, see row 37.** |"),
    "| 37 |": (
        " **STATUS 2026-11-15 (test build 20): THE TOY CANNON HAS A VIEW FOR EACH PLAYER** (the own-screen option "
        "`--cannon2view`: camera 2 is the game's still view, moved to player 2's cannon). The three small games were "
        "also started by the story's own jump (\"Type 2\"), and the sidecar from its story scene; walking into the "
        "toy cannon and the carpet escape through the story's talk point cannot be done by a test script (the test "
        "start has not the story's progress). This row's rule is taken for a boss's hold too: while both heroes are "
        "held, both controllers count (glue 68, row 9). (docs\\STATE.md, Ninth round, parts 95, 97, 98, 100.) |"),
    "| 39 |": (
        " **STATUS 2026-11-15, later (test build 20): THE REST IS BUILT.** Player 2 has his own item places, his own "
        "stock of the fight items and his own shortcuts (glue 62) and his own Keyblade (glue 63; glue 64 binds a "
        "weapon to its files by name, register F8). What the game gives is there for each player: a fight item goes "
        "into both stocks; a Keyblade, an armour or an accessory comes twice into the bag. Still common, and said "
        "so in the read-me: the bag itself (with two of each thing given), the wallet (a purchase gives the thing "
        "to both), the materials, a Drive Form's second Keyblade. (docs\\STATE.md, Ninth round, parts 89 to 92 "
        "and 95.) |"),
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
last = max(i for i, l in enumerate(lines) if l.startswith("| 51 |"))
row52 = ("| 52 | TEST BUILD 20 (ninth round, 2026-11-15) | Build 19 + seven glues (62 to 68; `tools\\merge\\merge_v7.py --ownrec "
         "--ownmenu --together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner --ownabil "
         "--holdwatch --itemsync --ownitems --ownkey --bindname --holdpair --ship2score --trickguard --holdpads`) and "
         "the own-screen option `--cannon2view` of `tools\\own\\make_own.py`: player 2's own item places, fight items, "
         "shortcuts and Keyblade (row 39); both heroes inside the same hold of a boss, the Groundshaker's cause "
         "cured, Luxord's tricks, both controllers in a hold (row 9); a view for each player at the toy cannon (rows "
         "36, 37); a score for each player in the Gummi flight (row 35). The disc file is still the one of build "
         "12. Details and evidence: docs\\STATE.md, section \"Ninth round\", parts 89 to 101. |")
lines.insert(last + 1, row52)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: the rows 9, 35, 36, 37 and 39 have their build 20 status, row 52 is added")
