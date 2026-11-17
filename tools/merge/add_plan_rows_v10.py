"""One-off: KH2-COOP-PLAN.md after test build 18 (eighth round): a status sentence at the end of rows 9, 36, 37 and
39, and a new row 50. (Written for build 17 first; that build was never given out, see row 50. Rewritten three
times before its first run.) Run once:  python -I tools/merge/add_plan_rows_v10.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 50 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 9 |": (
        " **STATUS 2026-11-15 (test build 18): THE OTHER FIGHTS WERE PLAYED ON PURPOSE WITH TWO HEROES** (ten boss "
        "rooms, both players pressing, 20,000 frames each: the Dark Thorn, Cerberus, Scar, Xaldin, Demyx twice, the "
        "Hydra, the Groundshaker, the last Xemnas, the armoured Xemnas). Read in their scripts: the moves these "
        "bosses force on a hero are HOLDS of one hero by the boss's body (a grab, a ride, a throw), not a "
        "face-to-face struggle like Shan-Yu's clash; the boss takes either hero and the other stays free and "
        "fights. A FAULT WAS FOUND: at the Groundshaker one step of a hold landed on the free hero, who was then "
        "held for ever (builds 12 to 17). Glue 60: a hero in one and the same captured motion for 1,800 steps (a "
        "minute) is let go; shown with a stray capture made on purpose (without the glue he stays frozen, with "
        "it he plays on). Glue 59 (send the capture to the held hero) was tried first and made the Hydra worse; "
        "no build uses it. \"Both heroes inside the same hold\" is NOT "
        "built for these fights: it would put two heroes into one hand; that is my reading, and whether these "
        "holds may stay one hero's is the user's to say (REQUIREMENT-full-parity.md). "
        "(docs\\STATE.md, Eighth round, parts 79 to 83; docs\\ROW9-PAIRED-MOVES.md.) |"),
    "| 36 |": (
        " **STATUS 2026-11-14, later (test build 18): the toy cannon, the sidecar and the carpet escape have a "
        "second hero now, see row 37.** |"),
    "| 37 |": (
        " **STATUS 2026-11-14 (test build 18): THE THREE ONE-HERO SMALL GAMES HAVE A HERO OR A VEHICLE FOR EACH "
        "PLAYER.** The second one is MADE AT RUN TIME with the game's own \"make an object\" (no new disc; the "
        "build's identity rule makes it player 2's). The carpet escape: he gets the escape's own state and a "
        "second escape carpet that follows him. The sidecar: he gets the sidecar's own state. The toy cannon: "
        "a second cannon; one shared view there, because the cannon's camera kind exists for camera 1 only. "
        "In every other scene without a hero for player 2 his controller still drives the one hero, as before. "
        "All three were played by scripts: the escape to its end, the sidecar through a Game Over and "
        "\"Continue\", the toy cannon to its end and on into the next room. Not yet played by two people, and "
        "not from the story (the test runs jump into the rooms). "
        "(docs\\STATE.md, Eighth round, parts 70, 71, 73, 74 and 76 to 78.) |"),
    "| 39 |": (
        " **STATUS 2026-11-15 (test build 18): STAGE 1b IS BUILT AND VERIFIED: PLAYER 2 SWITCHES HIS OWN ABILITIES.** "
        "Read: the ability list only grows (a new ability takes the first empty place), so his switches are one "
        "bit per place: five shorts with a mark, kept in King Mickey's record in the save data (item places he "
        "never has), saved with the game's own save. His pause menu shows and edits his; in a fight each hero "
        "has the abilities of his own switches; an ability the game gives goes to both. STILL OPEN under this "
        "row: own Keyblade, own item places, own bag and wallet, \"everything given goes to each\" for items and "
        "munny. (docs\\STATE.md, Eighth round, parts 79 to 83.) |"),
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
last = max(i for i, l in enumerate(lines) if l.startswith("| 49 |"))
row50 = ("| 50 | TEST BUILD 18 (eighth round, 2026-11-15) | Build 16 + seven glues (53 to 58 and 60; `tools\\merge\\merge_v7.py "
         "--ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner "
         "--ownabil --holdwatch`) and the own-screen option `--cannon1view` of `tools\\own\\make_own.py`: a second "
         "hero, made at run time, in the carpet escape, on the sidecar and at the toy cannon (plan rows 36 and 37); "
         "player 2's own ability switches (row 39); no hero is held for ever (row 9). BUILD 17 was "
         "build 16 + the glues 53 to 56; it was packaged and rehearsed, but a 60,000-frame run of the toy cannon "
         "then showed 50 fault lines at the game's end (the HUD's owner became a cannon, which has no HP record; "
         "cured by glue 57); it was never given out. The disc file is still the one of build 12. Details and "
         "evidence: docs\\STATE.md, section \"Eighth round\", parts 70 to 83. |")
lines.insert(last + 1, row50)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: rows 9, 36, 37 and 39 have their build 18 status, row 50 is added")
