"""One-off: KH2-COOP-PLAN.md after test build 21 (ninth round, after the user's answers of 2026-11-15): a status sentence at the
end of the rows 9, 35 and 39, and a new row 53. Run once:  python -I tools/merge/add_plan_rows_v13.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 53 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 35 |": (
        " **STATUS 2026-11-15, later (test build 21): build 20's second score row made some Gummi routes fly a little "
        "differently (its ten pictures lay in the flight module's own heap); they lie in the patch's own memory now, "
        "and route 8 is build 19's to the point again.** (docs\\STATE.md, Ninth round, parts 103, 104, 106, 107.) |"),
    "| 9 |": (
        " **STATUS 2026-11-15, night (test build 21; the user's items 1 and 4 of that evening): A BOSS'S AUTOMATIC GRAB TAKES ONLY "
        "THE HERO IT AIMS AT; THE OTHER PLAYER KEEPS FIGHTING. Every boss capture in the 40 fights and the ten boss rooms is "
        "single-target except the last Xemnas's laser dome (move 0x106), the game's own party move: there both heroes stand "
        "in it, each player has his own Reflect in his own menu, a press of either counts once (the dome's pieces run on "
        "player 1's hero, the one its lasers aim at; the mirror gives each move to player 2's hero) and the dome ends once. "
        "Glue 68 (the two controllers made one in a hold) is left out: each player keeps his own controller, one press never "
        "counts twice (also measured in Shan-Yu's clash: the push count goes up once a push). Shan-Yu's old stray calls: 0 in "
        "the runs. The Samurai duel by player 2: verified. The last Xemnas's Riku part with one hero held: the held hero's "
        "player plays Riku and ended the part with his own command in a test (run rs4, eh20 98). NOT VERIFIED (for the "
        "user's playthrough): the Large Body's Full Swing (never offered in the tests). Mail Delivery and the skate "
        "challenges keep build 20's pair (a board or gimmick is no enemy).** (docs\\STATE.md, Ninth round, parts 110 to 115.) |"),
    "| 39 |": (
        " **STATUS 2026-11-15, later (test build 21; the user's answer D of that day: \"each player his own bag and wallet; "
        "the money they gain goes to both; while they spend it each one alone\"): OWN WALLET AND OWN BAG ARE BUILT.** "
        "Munny the game gives goes into both wallets; a shop or the Moogle is the shop of the player who opened it "
        "(his munny, his things); player 2's pause menu shows his munny and his bag; what the game gives goes into "
        "both bags, once into each. His bag (Keyblades, armour, accessories, materials) lives in King Mickey's "
        "ability places 16 to 79 (read-proven: never cleared after a New Game, never read as abilities) and keeps up "
        "to 7 of one Keyblade, armour or accessory. Still common: Tent, Boosts, Drive recoveries, the helpers' and "
        "guests' weapons, recipes, Torn Pages, elements, key items. Also cured: player 2 could not finish a purchase "
        "(his buttons did nothing in \"Buy how many?\"). (docs\\STATE.md, Ninth round, parts 105 to 108.) |"),
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
last = max(i for i, l in enumerate(lines) if l.startswith("| 52 |"))
row53 = ("| 53 | TEST BUILD 21 (ninth round, 2026-11-15) | Build 20 + three glues (69 to 71; `tools\\merge\\merge_v7.py ... --trickguard "
         "--holdshared --ownwallet --shoppad --ownbag`) and the sixty-sixth glue's sixth and seventh forms: player 2's own "
         "wallet and own bag (row 39), player 2's buttons in the shop's quantity box, the Gummi flight as the game's again "
         "(row 35), and the sixty-fifth glue's fifth form (row 9: a boss's grab takes only its target; the last Xemnas's "
         "laser dome takes both, each player with his own Reflect; glue 68 left out). Built and tested on Opus 5.5 after the "
         "user switched the session's model. The disc file is still the one of build 12. Details and evidence: "
         "docs\\STATE.md, section \"Ninth round\", parts 103 to 115. |")
lines.insert(last + 1, row53)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: the rows 9, 35 and 39 have their build 21 status, row 53 is added")
