"""One-off: the test package goes to BUILD 21 = build 20 + the glues 69 to 71 and the sixty-sixth glue's sixth and seventh
forms (docs/STATE.md, Ninth round, parts 105 to 109; the user's answer D of 2026-11-15: "each player his own bag and
wallet; the money they gain goes to both; while they spend it each one alone"):
  69 --ownwallet  player 2's own wallet: munny the game gives goes to both; a shop / the Moogle is the opener's
  70 --shoppad    player 2's buttons work in the shop's "Buy how many?" (in builds up to 20 he could not buy)
  71 --ownbag     player 2's own bag (Keyblades, armour, accessories, materials); what the game gives goes to both
  66 (forms 6, 7) the Gummi flight's extra score pictures no longer change the flight (route 8 is the game's again)
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v15-own (own
screens) and patches/merged-v15 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v15 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync --ownitems --ownkey --bindname --holdpair
--ship2score --trickguard --holdshared --ownwallet --shoppad --ownbag` and `tools/own/make_own.py patches/merged-v15-own
--base merged-v15 --cannon2view`. Build 20's patches/merged-v14 / merged-v14-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v21.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) >= 1:      # this pair is already in (a first run stopped half way)
            continue
        assert t.count(old) == 1, (path.name, t.count(old), old[:70])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


if "TEST BUILD 21" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 21")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v15", "merged-v15-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v14-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v15-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v14) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v15) + the same group"),
    ('make("patches/merged-v14-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v15-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v14-own, tools/own/make_own.py --base merged-v14 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v15-own, tools/own/make_own.py --base merged-v15 --cannon2view)")'),
    ('make("patches/merged-v14/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v15/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v14-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v15-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v14" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v15" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v14-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v15-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v14 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v15 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 20 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 21 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""(6) LUXORD'S TRICKS LET THE LOSER GO IN TIME (he could stand still for a minute). The same paragraph as (2).""",
     """(6) LUXORD'S TRICKS LET THE LOSER GO IN TIME (he could stand still for a minute). The same paragraph as (2).
NEW IN BUILD 21 (the disc file is still the same), four things:
(1) EACH PLAYER HAS HIS OWN WALLET AND HIS OWN BAG. Munny the game gives (enemies' munny balls, chests, rewards)
    goes into BOTH wallets in full; what a player buys he pays alone, from his own wallet, and it goes into his
    own bag. What the game gives (a Keyblade, an armour, an accessory, a material) goes into both bags. Read
    "PLAYER 2'S OWN GEAR" further down.
(2) PLAYER 2 CAN BUY IN A SHOP. Up to build 20 his buttons did nothing in "Buy how many?", so he could not
    finish a purchase. Now either player's buttons work there.
(3) THE GUMMI FLIGHT IS THE GAME'S AGAIN. Build 20's second score row made some routes fly a little
    differently (enemies came at other moments); found and cured, both scores stay.
(4) A BOSS'S GRAB TAKES ONLY THE HERO IT IS AIMED AT AGAIN; the other player keeps fighting. Only the last
    Xemnas's laser part takes both heroes, and there each player has his own "Reflect". Each player keeps his
    own controller in a hold. Read "BOSSES THAT HOLD A HERO" further down."""),
    ("""(2) A BOSS'S OWN GRAB, RIDE OR THROW TAKES BOTH HEROES, and lets both go together. Read "BOSSES THAT HOLD A
    HERO" further down.""",
     """(2) A BOSS'S OWN GRAB, RIDE OR THROW TOOK BOTH HEROES (changed again in build 21: read "BOSSES THAT HOLD A
    HERO" further down)."""),
    ("""- A boss move that grabs or carries a hero: UP TO BUILD 19 IT TOOK ONE HERO and the other stayed free. SINCE
  BUILD 20 IT TAKES BOTH HEROES: read "BOSSES THAT HOLD A HERO" further down. Since build 13 the move's green
  command is in the menu of the player whose hero the boss took (tested at Shan-Yu's gate clash: player 2
  alone can win it); since build 20 the other player's buttons count too while both heroes are held.""",
     """- A boss move that grabs or carries a hero: up to build 19 it took one hero; build 20 took both heroes; SINCE
  BUILD 21 IT TAKES THE HERO IT IS AIMED AT AGAIN (only the last Xemnas's laser part takes both): read "BOSSES
  THAT HOLD A HERO" further down. Since build 13 the move's green command is in the menu of the player whose
  hero the boss took (tested at Shan-Yu's gate clash: player 2 alone can win it)."""),
    ("""- BOSSES THAT HOLD A HERO (new in build 20). A BOSS'S OWN GRAB, RIDE OR THROW NOW TAKES BOTH HEROES. A boss's
  script is written for one hero; now, when it takes one hero (and that is not the answer to this hero's own
  green command), the other hero is put into the same hold, wherever he stands, every step of the hold is
  done for both, and both are let go together. Seen in the tests with two heroes: Cerberus, Scar, the Dark
  Thorn, the Groundshaker's ride (both ride), the armoured Xemnas, and the last Xemnas: his opening move, the
  part where Riku must free Sora (both heroes are held), the laser part at the end (both stand in it).
  WHILE A BOSS HOLDS BOTH HEROES, BOTH CONTROLLERS COUNT: the buttons and the stick of either player work for
  the hold (not START: each player's START stays his own). So in the last Xemnas's fight, when both heroes
  hang in his hold and Riku must free them, BOTH PLAYERS STEER RIKU (before, only the player whose hero
  Xemnas had picked could, and the other one waited).""",
     """- BOSSES THAT HOLD A HERO (changed in build 21). A BOSS'S GRAB, RIDE OR THROW TAKES ONLY THE HERO IT IS AIMED
  AT; THE OTHER PLAYER KEEPS FIGHTING. (Build 20 put the other hero into every hold too. Now a grab that aims
  at one hero takes that hero only, as the game.) In the last Xemnas's part where Riku must free Sora, the
  player whose hero Xemnas took plays Riku with his own controller, and the other player fights on.
  ONE SHARED MOVE TAKES BOTH HEROES: the last Xemnas's laser part at the end (the game itself puts the player
  and Riku into it). Both heroes stand in it and EACH PLAYER HAS HIS OWN "REFLECT" in his own menu: a press of
  either player makes both heroes reflect and counts once. When both press in the very same instant, that is
  one reflect.
  EACH PLAYER KEEPS HIS OWN CONTROLLER IN A HOLD (build 20 joined the two controllers while both heroes were
  held; that is gone). One press never counts twice."""),
    ("""  Level, the abilities learned and munny are common: one wallet. Each player has his own armour and
  accessories (since build 15), switches his own abilities (since build 19) and has his own Keyblade, item
  places, fight items and shortcuts (since build 20).""",
     """  Level and the abilities learned are common. Each player has his own armour and accessories (since build
  15), switches his own abilities (since build 19), has his own Keyblade, item places, fight items and
  shortcuts (since build 20) and his own wallet and bag (since build 21)."""),
    ("""- Both heroes pick up what enemies drop. HP and Drive go to the hero who took it; munny goes into the one wallet.""",
     """- Both heroes pick up what enemies drop. A ball's HP, MP or Drive goes to the hero who took it and to nobody
  else (tested for HP and MP balls taken by player 2; Drive balls did not drop in the tests); munny goes into
  BOTH wallets (since build 21; before: the one wallet)."""),
    ("""  STILL COMMON: the bag of Keyblades, armour and accessories (with two of each thing the game gives), the
  wallet (what one player buys, both get), the materials, the list of abilities learned, the Drive Forms'
  own abilities and a Drive Form's second Keyblade. In a new game, and in a save from an older build, player 2
  starts with the same Keyblade, item places, stock and shortcuts as player 1.""",
     """  SINCE BUILD 21 EACH PLAYER HAS HIS OWN WALLET AND HIS OWN BAG (Keyblades, armour, accessories and
  materials; the fight items had their own stock already). Munny the game gives goes into both wallets in full;
  what the game gives (a chest, a prize, a reward) goes into both bags, once into each (no longer two copies
  in one bag). A SHOP OR THE MOOGLE IS THE SHOP OF THE PLAYER WHO OPENED IT (with his Triangle): it shows HIS
  munny and HIS things; what he buys he pays from his wallet and it goes into his bag, what he sells leaves
  his bag and its munny goes into his wallet, and the Moogle uses his materials. Player 2's pause menu shows
  his munny and his bag. PLAYER 2'S BAG KEEPS UP TO 7 OF ONE KEYBLADE, ONE ARMOUR OR ONE ACCESSORY (and up to
  99 of one material, as the game); player 1's up to 99, as the game. A thing one player puts on Donald,
  Goofy or a guest comes back into the bag of the player who takes it off there.
  STILL COMMON: Tent, the Boosts and the Drive recoveries (they act on the one Sora and the party), Donald's,
  Goofy's and the guests' weapons, the recipes, Torn Pages, the magic elements and the key items, the list of
  abilities learned, the Drive Forms' own abilities and a Drive Form's second Keyblade. In a new game, and in
  a save from an older build, player 2 starts with the same Keyblade, item places, stock, shortcuts, munny and
  bag as player 1."""),
    ("""  GAME GIVES (a chest, a prize, a reward, a shop) IS THERE FOR EACH PLAYER: a fight item goes to both stocks,
  and a Keyblade, an armour or an accessory comes twice into the bag, so that each can wear one. The two""",
     """  GAME GIVES (a chest, a prize, a reward) IS THERE FOR EACH PLAYER: a fight item goes to both stocks, and
  (since build 21) a Keyblade, an armour, an accessory or a material into both bags. The two"""),
    ("""- Item drops (not the HP / munny balls) are probably still taken by player 1's hero only. Not tested.""",
     """- Item drops (not the HP / MP / munny balls): a material the game gives goes into both bags (since build 21).
  Whether player 2 can pick up a dropped material himself is not tested yet (no material dropped in the tests)."""),
    ("""- Not met by any test script, so not tested: the Large Body's and the Samurai's green commands for player 2.""",
     """- THE SAMURAI'S DUEL WORKS FOR PLAYER 2 in the tests (build 21): "Duel Stance" and "The End" are in his own menu,
  and the Samurai falls to his finish. Not met by any test script: the Large Body's green command ("Full
  Swing") for player 2."""),
    ("them in the pause menu when HE opened it (START on his controller), under Items, then Sora. The bag is common.",
     "them in the pause menu when HE opened it (START on his controller), under Items, then Sora. (Since build 21\n"
     "each player also has his own bag.)"),
    ("  is his alone. When player 1 presses START it shows player 1's. Both take from the one common bag. Each hero",
     "  is his alone. When player 1 presses START it shows player 1's. Each takes from his own bag (since build 21;\n"
     "  before: the one common bag). Each hero"),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 20 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 21 (OWN SCREENS)"),
])
print("package tooling and read-me are build 21 (disc v5, patches merged-v15 / merged-v15-own)")
