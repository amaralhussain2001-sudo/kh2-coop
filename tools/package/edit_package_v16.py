"""One-off: the test package goes to BUILD 16 (eighth round: both heroes in Shan-Yu's clash, plan row 9 second
half; player 2's Gummi ship can be hit, plan row 35; a carpet under player 2's hero, plan row 36). THE DISC FILE IS
STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v10-own (own screens) and
patches/merged-v10 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v10 --ownrec --ownmenu --together --ship2hit --carpet2` and
`tools/own/make_own.py patches/merged-v10-own --base merged-v10`. Build 15's patches/merged-v9 / merged-v9-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v16.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 16" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 16")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v10", "merged-v10-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v9-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v10-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v9) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v10) + the same group"),
    ('make("patches/merged-v9-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v10-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v9-own, tools/own/make_own.py --base merged-v9)")',
     '     "OWN SCREENS build (patches/merged-v10-own, tools/own/make_own.py --base merged-v10)")'),
    ('make("patches/merged-v9/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v10/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v9-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v10-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v9" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v10" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v9-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v10-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v9 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v10 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 15 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 16 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 15 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 16 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.""",
     """NEW IN BUILD 16 (the disc file is still the same), three things:
(1) BOTH HEROES IN SHAN-YU'S CLASH. When Shan-Yu locks blades with one hero at the palace gate and the other hero
    stands near, the other hero joins the clash: he stands beside his friend, "Press" is in HIS menu too, and
    his own Triangle pushes. Read "SHAN-YU'S CLASH" further down.
(2) PLAYER 2'S GUMMI SHIP CAN BE HIT and has its own hull. The mission is over when EITHER ship falls. The one
    hull gauge shows the weaker ship. A repair mends both ships. Read "THE GUMMI SHIP" further down.
(3) A MAGIC CARPET FOR EACH HERO: on the carpet rides player 2's hero now has his own carpet under him.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter."""),
    ("""  can go on fighting. Two heroes inside the same move at once is not built.""",
     """  can go on fighting. Two heroes inside the same move at once is built for ONE move so far, Shan-Yu's clash
  (next point); for every other boss the move still takes one hero.
- SHAN-YU'S CLASH (since build 16). When Shan-Yu locks blades with one hero and the other hero is up, free and
  near (about 500 units, a few steps), the other hero is put beside and a little behind his friend and is in
  the clash too. Both screens show the clash. Each player has "Press" (and at the end "Takedown") in his own
  menu, and each player's Triangle pushes. One press makes both heroes push and counts once, and the clash
  lasts as long as in the game, so two players who both press win it sooner than one. A hero who is far away
  when the clash starts stays free and can go on fighting. The falcon's lift takes one hero only, as before.
  Tested with scripts for both players, in both roles; not yet played by two people."""),
    ("""  What his ship does not have yet: the enemies cannot damage it, and the flight is lost when PLAYER 1's ship
  is destroyed. There is one hull gauge (player 1's ship). Both ships look the same; player 2's starts a
  little to the right.""",
     """  THE GUMMI SHIP SINCE BUILD 16: THE ENEMIES CAN DAMAGE PLAYER 2'S SHIP, and it has its own hull. The flight is
  lost when EITHER ship is destroyed (the same rule as on the Light Cycles). There is still one hull gauge: it
  shows the hull of the WEAKER ship, so both players see how near the end is, but it does not say whose ship
  that is. A repair item mends both ships. One score for both. Both ships look the same; player 2's starts a
  little to the right. Tested by scripts (both ships are hit; either ship falling ends the flight; all nine
  routes flown with two ships); not yet played by two people."""),
    ("""  Two things to know: on the carpet, player 2's hero flies in the riding pose WITHOUT a carpet under him (the
  one carpet stays under player 1's hero); it looks odd and works. On the Light Cycle the ride is over when
  EITHER cycle is destroyed, as the game does it for one rider; nobody can be picked up there.""",
     """  SINCE BUILD 16 EACH HERO HAS HIS OWN CARPET on the carpet rides (before, player 2's hero flew in the riding
  pose with nothing under him). One thing to know: on the Light Cycle the ride is over when EITHER cycle is
  destroyed, as the game does it for one rider; nobody can be picked up there."""),
])
print("package tooling and read-me are build 16 (disc v5, patches merged-v10 / merged-v10-own)")
