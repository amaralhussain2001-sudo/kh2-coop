"""One-off: the test package goes to BUILD 18 = build 17 + three glues (docs/STATE.md, Eighth round, parts 76 to 82):
  57 --hudowner   the fault lines at the end of the toy cannon's game with two cannons are gone;
  58 --ownabil    player 2 switches his own abilities on and off (plan row 39, stage 1b);
  60 --holdwatch  no hero is held for ever: a hero in one and the same captured motion for 1,800 steps (a
                  minute) is let go (the Groundshaker left a hero frozen for the rest of the fight).
                  (Glue 59, --onevictim, was tried for that and made the Hydra worse: no build uses it.)
Build 17 (package id efd72bf53d96 of 2026-11-14 22:09) was never given out; for the user build 18 is the build
after 16, so the read-me's "NEW IN BUILD 17" becomes "NEW IN BUILD 18".
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v12-own (own
screens) and patches/merged-v12 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v12 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake --hudowner --ownabil --holdwatch` and
`tools/own/make_own.py patches/merged-v12-own --base merged-v12 --cannon1view`.
Build 17's patches/merged-v11 / merged-v11-own and build 16's merged-v10 / merged-v10-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
(Written first for "build 17 + glue 57" only; rewritten before its first run.)
  python -I tools/package/edit_package_v18.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 18" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 18")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v12", "merged-v12-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v11-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v12-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v11) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v12) + the same group"),
    ('make("patches/merged-v11-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v12-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v11-own, tools/own/make_own.py --base merged-v11 --cannon1view)")',
     '     "OWN SCREENS build (patches/merged-v12-own, tools/own/make_own.py --base merged-v12 --cannon1view)")'),
    ('make("patches/merged-v11/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v12/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v11-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v12-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v11" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v12" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v11-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v12-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v11 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v12 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 17 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 18 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""NEW IN BUILD 17 (the disc file is still the same): THE THREE SMALL GAMES THAT HAD ONE HERO FOR BOTH PLAYERS
NOW HAVE ONE FOR EACH: in the carpet escape from the ruins player 2 flies his own hero on his own carpet; on
the sidecar near the end player 2 has his own machine; at the toy cannon (Gift Wrapping) player 2 has his own
cannon. Read "THE THREE SMALL GAMES" further down.""",
     """NEW IN BUILD 18 (the disc file is still the same), three things:
(1) THE THREE SMALL GAMES THAT HAD ONE HERO FOR BOTH PLAYERS NOW HAVE ONE FOR EACH: in the carpet escape from
    the ruins player 2 flies his own hero on his own carpet; on the sidecar near the end player 2 has his own
    machine; at the toy cannon (Gift Wrapping) player 2 has his own cannon. Read "THE THREE SMALL GAMES".
(2) PLAYER 2 SWITCHES HIS OWN ABILITIES ON AND OFF, in the pause menu when HE opened it, under "Abilities",
    then "Sora". Read "PLAYER 2'S OWN GEAR" further down.
(3) NO HERO STAYS HELD FOR EVER. At the Groundshaker a hero could stay frozen for the rest of the fight
    (builds 12 to 16); now he is let go after a minute. Read "BOSSES THAT HOLD A HERO" further down."""),
    ("  Level, skills, equipment, items and munny are common: one wallet, one item stock, the same abilities.",
     """  Level, the abilities learned, the Keyblade, items and munny are common: one wallet, one item stock. Each
  player has his own armour and accessories (since build 15) and switches his own abilities (since build 18)."""),
    ("- THE THREE SMALL GAMES (since build 17). The carpet escape from the ruins, the toy cannon (Gift Wrapping) and",
     "- THE THREE SMALL GAMES (since build 18). The carpet escape from the ruins, the toy cannon (Gift Wrapping) and"),
    ("""  Tested by scripts (the escape flown to its end; the sidecar through a Game Over and "Continue"); the end of
  the toy cannon's game was not reached by a script. Not yet played by two people.""",
     """  Tested by scripts (the escape flown to its end; the sidecar through a Game Over and "Continue"; the toy
  cannon played to its end and on into the next room). Not yet played by two people."""),
    ("""  STILL COMMON: the Keyblade, the abilities and the items in the item places. A change of these in either menu
  is for both heroes.""",
     """  SINCE BUILD 18 THE ABILITIES' SWITCHES ARE HIS OWN TOO. When PLAYER 2 opened the menu, "Abilities", then
  "Sora" shows which abilities HE has switched on and his own AP count; "Equip" / "Don't Equip" there changes
  only his. In a fight each hero has the abilities of his own switches. Every ability the game gives is given
  to both, and switched on for him when the game switches it on. In a new game, and in a save from an older
  build, he starts with the same switches as player 1.
  STILL COMMON: the Keyblade, the items in the item places, the list of abilities learned, the Drive Forms'
  own abilities. A change of these in either menu is for both heroes."""),
    ("""  Small things: player 2's AP comes from his own accessories while the abilities are the common ones, so his
  menu can show more AP in use than he has. A shop marks player 1's things as "equipped". While a menu is""",
     """  Small things: when the game gives an ability switched on, player 2 gets it switched on even if his own AP
  is used up; his menu then shows more AP in use than he has until he switches something off. A shop marks
  player 1's things as "equipped". While a menu is"""),
    ("""- SINCE BUILD 14: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK (both in The World That Never Was) work with two""",
     """- BOSSES THAT HOLD A HERO (since build 18). A boss's script is written for one hero. When a boss held one hero
  and one step of the hold landed on the other, free hero, nobody ever let that hero go: seen once at the
  Groundshaker in the Pride Lands, where a hero stood frozen for the rest of the fight (builds 12 to 16). NOW A
  HERO WHO STANDS IN ONE AND THE SAME HELD POSE FOR A MINUTE IS LET GO and can play on. (A minute is long, but
  no ordinary hold of a boss lasts a third of that, so nothing else is cut short.) Played on purpose by
  scripts with two heroes, both pressing: the Dark Thorn, Cerberus, Scar, Xaldin, Demyx (both fights), the
  Hydra, the Groundshaker, the last Xemnas and the armoured Xemnas: the boss takes either hero, the other
  stays free, and every hold ends. Not yet played by two people. If a hero is let go only after that
  minute, or not at all, tell me the fight.
- SINCE BUILD 14: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK (both in The World That Never Was) work with two"""),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 17 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 18 (OWN SCREENS)"),
])
print("package tooling and read-me are build 18 (disc v5, patches merged-v12 / merged-v12-own)")
