"""One-off: the test package goes to BUILD 24 = build 23 + glue 78 --gummitag (docs/STATE.md, Tenth round, parts 134 to 136; the
user's word "okay do 8 9 10 also 7"): in the Gummi Ship, the points of weapons other than the cannons go to the ship that fired
(build 23 and older: always to player 1).
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v18-own (own screens) and
patches/merged-v18 (shared-screen fallback), written by `tools/merge/merge_v7.py patches/merged-v18 <build 23's options> --gummitag`
and `tools/own/make_own.py patches/merged-v18-own --base merged-v18 --cannon2view`. Build 23's merged-v17 / merged-v17-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v24.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 24" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 24")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v18", "merged-v18-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v17-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v18-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v17) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v18) + the same group"),
    ('make("patches/merged-v17-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v18-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v17-own, tools/own/make_own.py --base merged-v17 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v18-own, tools/own/make_own.py --base merged-v18 --cannon2view)")'),
    ('make("patches/merged-v17/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v18/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v17-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v18-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v17" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v18" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v17-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v18-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v17 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v18 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 23 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 24 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""NEW IN BUILD 23 (the disc file is still the same), one fix:""",
     """NEW IN BUILD 24 (the disc file is still the same), one change:
(1) THE GUMMI SHIP: the points of weapons OTHER THAN THE CANNONS now go to the ship that fired them (before, they always
    counted for player 1). Tested: two other weapon kinds, each fired by player 1 only, by player 2 only and by both: each
    ship's points to its own player; the cannons exactly as in build 23; no fault. Still player 1's, as before: points
    from ramming and from a few special shots.
    ALSO TESTED NOW, NOTHING TO CHANGE: doors in a Drive Form keep a copy of the Keyblade per door in the ORIGINAL game
    too (tested with one hero), and 16 doors in a row with forms never ran out of memory; the boss helpers that no test
    could reach before (Luxord's, the Twin Lords', Zexion's and two others) were met with two heroes, no fault; Luxord's
    and the two others grabbed player 2 as well as player 1.
NEW IN BUILD 23 (the disc file is still the same), one fix:"""),
    ("""  called it. Player 2's gauge after a load is not the one from the moment of saving (a saved game holds
  player 1's values only).""",
     """  called it. Since build 22 player 2's Drive gauge after a load is his own saved one (before: player 1's)."""),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 23 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 24 (OWN SCREENS)"),
])
print("package tooling and read-me are build 24 (disc v5, patches merged-v18 / merged-v18-own)")
