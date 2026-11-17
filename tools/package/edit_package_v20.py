"""One-off: the test package goes to BUILD 20 = build 19 + the glues 62 to 68 of the ninth round and the own-screen
option --cannon2view (docs/STATE.md, Ninth round, parts 89 to 101):
  62 --ownitems   player 2's own item places, stock of the fight items, shortcuts; what the game gives is there for each
  63 --ownkey     player 2's own Keyblade                      64 --bindname   a weapon finds its files by name (register F8)
  65 --holdpair   a boss's own grab takes both heroes; the Groundshaker's cause cured; "let him go" that works
  66 --ship2score the Gummi flight: a score for each player, a digit at the hull gauge
  67 --trickguard Luxord does not flinch while a hero stands in his trick (the long hold at Data Luxord is cured)
  68 --holdpads   while a boss holds both heroes, both controllers count (both players steer Riku at the last Xemnas)
  --cannon2view   the toy cannon: a view for each player
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v14-own (own
screens) and patches/merged-v14 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v14 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync --ownitems --ownkey --bindname --holdpair
--ship2score --trickguard --holdpads` and `tools/own/make_own.py patches/merged-v14-own --base merged-v14 --cannon2view`.
Build 19's patches/merged-v13 / merged-v13-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v20.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 20" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 20")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v14", "merged-v14-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v13-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v14-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v13) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v14) + the same group"),
    ('make("patches/merged-v13-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v14-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v13-own, tools/own/make_own.py --base merged-v13 --cannon1view)")',
     '     "OWN SCREENS build (patches/merged-v14-own, tools/own/make_own.py --base merged-v14 --cannon2view)")'),
    ('make("patches/merged-v13/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v14/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v13-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v14-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v13" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v14" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v13-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v14-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v13 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v14 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 19 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 20 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""(4) PLAYER 2'S "ITEMS" LIST IS RIGHT AGAIN. In builds 15 and 16 his list could still show an item that had
    already been used, and let him take it. Read "PLAYER 2'S OWN GEAR" further down.""",
     """(4) PLAYER 2'S "ITEMS" LIST IS RIGHT AGAIN. In builds 15 and 16 his list could still show an item that had
    already been used, and let him take it. Read "PLAYER 2'S OWN GEAR" further down.
NEW IN BUILD 20 (the disc file is still the same), six things:
(1) PLAYER 2 HAS HIS OWN KEYBLADE, HIS OWN ITEM PLACES, HIS OWN FIGHT ITEMS AND HIS OWN SHORTCUTS, each chosen in
    his own menu; and whatever the game gives is there for each player. Read "PLAYER 2'S OWN GEAR".
(2) A BOSS'S OWN GRAB, RIDE OR THROW TAKES BOTH HEROES, and lets both go together. Read "BOSSES THAT HOLD A
    HERO" further down.
(3) THE GROUNDSHAKER'S FROZEN HERO IS CURED AT ITS CAUSE (the same paragraph).
(4) THE TOY CANNON: EACH PLAYER HAS HIS OWN VIEW. Read "THE THREE SMALL GAMES".
(5) THE GUMMI SHIP: A SCORE FOR EACH PLAYER, and a digit at the hull gauge that says whose ship it shows. Read
    "THE GUMMI SHIP" further down.
(6) LUXORD'S TRICKS LET THE LOSER GO IN TIME (he could stand still for a minute). The same paragraph as (2)."""),
    ("""  Level, the abilities learned, the Keyblade, items and munny are common: one wallet, one item stock. Each
  player has his own armour and accessories (since build 15) and switches his own abilities (since build 19).""",
     """  Level, the abilities learned and munny are common: one wallet. Each player has his own armour and
  accessories (since build 15), switches his own abilities (since build 19) and has his own Keyblade, item
  places, fight items and shortcuts (since build 20)."""),
    ("""  lost when EITHER ship is destroyed (the same rule as on the Light Cycles). There is still one hull gauge: it
  shows the hull of the WEAKER ship, so both players see how near the end is, but it does not say whose ship
  that is. A repair item mends both ships. One score for both. Both ships look the same; player 2's starts a
  little to the right. Tested by scripts (both ships are hit; either ship falling ends the flight; all nine
  routes flown with two ships); not yet played by two people.""",
     """  lost when EITHER ship is destroyed (the same rule as on the Light Cycles). There is still one hull gauge: it
  shows the hull of the WEAKER ship, so both players see how near the end is. SINCE BUILD 20 A DIGIT LEFT OF
  THE GAUGE SAYS WHOSE SHIP THAT IS (1 or 2), AND EACH PLAYER HAS HIS OWN SCORE: the number in the "SCORE" frame
  is player 1's points, the number to the right of the frame is player 2's. A cannon shot's points go to the
  ship that fired it; the points of other weapons (lasers and the like) cannot be told apart yet and go to
  player 1's number. The flight's result and its medals use the sum, as before. A repair item mends both
  ships. Both ships look the same; player 2's starts a little to the right. Tested by scripts (both ships
  are hit; either ship falling ends the flight; all nine routes flown with two ships; only player 1 firing,
  only player 2 firing, both firing); not yet played by two people."""),
    ("""  turned and fired by its own controller; there BOTH SCREENS SHOW THE SAME PICTURE (the cannons from behind),
  the score and the toy count are for both, and "Reload" loads both.""",
     """  turned and fired by its own controller; SINCE BUILD 20 EACH PLAYER HAS HIS OWN VIEW: the game's view from
  behind the cannon, centred on HIS cannon. The score and the toy count are for both, and "Reload" loads both."""),
    ("""  STILL COMMON: the Keyblade, the items in the item places, the list of abilities learned, the Drive Forms'
  own abilities. A change of these in either menu is for both heroes. THE ITEMS IN THE ITEM PLACES ARE ONE SET
  FOR BOTH: a Potion either player uses is gone for both, and each player's "Items" list shows what is left.
  (In builds 15 and 16 player 2's list kept showing an item that was gone; cured in build 19.)""",
     """  SINCE BUILD 20 HIS KEYBLADE, HIS ITEM PLACES, HIS FIGHT ITEMS AND HIS SHORTCUTS ARE HIS OWN TOO. When PLAYER
  2 opened the menu, "Items", then "Sora" shows HIS Keyblade and HIS item places, and "Customize" his own four
  shortcuts. Each player has his own stock of the fight items (Potion, Hi-Potion, Ether, Elixir, Mega-Potion,
  Mega-Ether, Megalixir): what one player uses or puts into a place is not taken from the other. WHATEVER THE
  GAME GIVES (a chest, a prize, a reward, a shop) IS THERE FOR EACH PLAYER: a fight item goes to both stocks,
  and a Keyblade, an armour or an accessory comes twice into the bag, so that each can wear one. The two
  heroes can carry different Keyblades; a Keyblade that the story itself puts into the hero's hand goes into
  both hands.
  STILL COMMON: the bag of Keyblades, armour and accessories (with two of each thing the game gives), the
  wallet (what one player buys, both get), the materials, the list of abilities learned, the Drive Forms'
  own abilities and a Drive Form's second Keyblade. In a new game, and in a save from an older build, player 2
  starts with the same Keyblade, item places, stock and shortcuts as player 1."""),
    ("""- BOSSES THAT HOLD A HERO (since build 19). A boss's script is written for one hero. When a boss held one hero
  and one step of the hold landed on the other, free hero, nobody ever let that hero go: seen once at the
  Groundshaker in the Pride Lands, where a hero stood frozen for the rest of the fight (builds 12 to 16). NOW A
  HERO WHO STANDS IN ONE AND THE SAME HELD POSE FOR A MINUTE IS LET GO and can play on. (A minute is long, but
  no ordinary hold of a boss lasts a third of that, so nothing else is cut short.) Played on purpose by
  scripts with two heroes, both pressing: the Dark Thorn, Cerberus, Scar, Xaldin, Demyx (both fights), the
  Hydra, the Groundshaker, the last Xemnas and the armoured Xemnas: the boss takes either hero, the other
  stays free, and every hold ends. Not yet played by two people. If a hero is let go only after that
  minute, or not at all, tell me the fight.""",
     """- BOSSES THAT HOLD A HERO (new in build 20). A BOSS'S OWN GRAB, RIDE OR THROW NOW TAKES BOTH HEROES. A boss's
  script is written for one hero; now, when it takes one hero (and that is not the answer to this hero's own
  green command), the other hero is put into the same hold, wherever he stands, every step of the hold is
  done for both, and both are let go together. Seen in the tests with two heroes: Cerberus, Scar, the Dark
  Thorn, the Groundshaker's ride (both ride), the armoured Xemnas, and the last Xemnas: his opening move, the
  part where Riku must free Sora (both heroes are held), the laser part at the end (both stand in it).
  WHILE A BOSS HOLDS BOTH HEROES, BOTH CONTROLLERS COUNT: the buttons and the stick of either player work for
  the hold (not START: each player's START stays his own). So in the last Xemnas's fight, when both heroes
  hang in his hold and Riku must free them, BOTH PLAYERS STEER RIKU (before, only the player whose hero
  Xemnas had picked could, and the other one waited).
  NOT TAKEN TOGETHER, on purpose: a move that a hero starts with his OWN green command (Xaldin's jumps, Demyx's
  water forms): he does it alone, and the other player can press the same command for himself. A hero who is
  down is not taken. Shan-Yu's hold has its own rule, as before.
  THE GROUNDSHAKER'S FROZEN HERO (builds 12 to 16) IS CURED AT ITS CAUSE: its shake-off captured whichever hero it
  hit, also the one who stood beside the ride, and nothing ever let that hero go. That capture is no longer
  made. Two safety nets stay: a hero left behind in a hold is thrown off about a second after the other one
  is free, and a hero who stands in one and the same held pose for a minute is thrown off too.
  LUXORD'S TRICKS (both fights): a hero who lost a card or command trick could stand still for up to a minute
  (builds 14 to 19), because the OTHER hero's hit on Luxord broke off the very act that turns the loser into
  a card or a die and lets him go. Cured: while a hero stands in Luxord's trick, a hit still takes Luxord's HP
  but does not make him flinch. The loser is let go after two to seven seconds, as the game means it.
  Not yet played by two people. If a hero is let go only after a minute, or not at all, tell me the fight."""),
    ("""- A boss move that grabs or carries a hero takes ONE hero. Its opening moves always took player 1's hero in the
  first big boss fight of the Roxas part; later moves take whoever the boss reaches.
  SINCE BUILD 13 the move's green command is in the menu of the player whose hero is in the move, and HIS
  buttons count (tested at Shan-Yu's gate clash: player 2 alone can win it). The other hero stays free and
  can go on fighting. Two heroes inside the same move at once is built for ONE move so far, Shan-Yu's clash
  (next point); for every other boss the move still takes one hero.""",
     """- A boss move that grabs or carries a hero: UP TO BUILD 19 IT TOOK ONE HERO and the other stayed free. SINCE
  BUILD 20 IT TAKES BOTH HEROES: read "BOSSES THAT HOLD A HERO" further down. Since build 13 the move's green
  command is in the menu of the player whose hero the boss took (tested at Shan-Yu's gate clash: player 2
  alone can win it); since build 20 the other player's buttons count too while both heroes are held.
  Shan-Yu's clash has its own rule (next point)."""),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 19 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 20 (OWN SCREENS)"),
])
print("package tooling and read-me are build 20 (disc v5, patches merged-v14 / merged-v14-own)")
