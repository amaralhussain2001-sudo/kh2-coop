"""One-off: the test package goes to BUILD 15 (eighth round, plan row 39 stage 1a). THE DISC FILE IS STILL "TEST v5";
only the patch files change: the package now takes patches/merged-v9-own (own screens) and patches/merged-v9
(shared-screen fallback), written by `tools/merge/merge_v7.py patches/merged-v9 --ownrec --ownmenu` and
`tools/own/make_own.py patches/merged-v9-own --base merged-v9`. Build 14's patches/merged-v8 / merged-v8-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v15.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 15" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 15")     # (the read-me is the LAST file edited: the guard holds only after a full run)

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v8-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v9-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v8) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v9) + the same group"),
    ('make("patches/merged-v8-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v9-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v8-own, tools/own/make_own.py --base merged-v8)")',
     '     "OWN SCREENS build (patches/merged-v9-own, tools/own/make_own.py --base merged-v9)")'),
    ('make("patches/merged-v8/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v9/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v8-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v9-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v8" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v9" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v8-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v9-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v8 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v9 lines")'),
])
edit(START, [
    ("   BUILDS 13 AND 14 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 15 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 14 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 15 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.""",
     """NEW IN BUILD 15 (the disc file is still the same): PLAYER 2 HAS HIS OWN ARMOUR AND ACCESSORIES. He chooses
them in the pause menu when HE opened it (START on his controller), under Items, then Sora. The bag is common.
IN A SAVE FROM AN OLDER BUILD PLAYER 2 STARTS WITH NOTHING ON: read "PLAYER 2'S OWN GEAR" further down.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter."""),
    ("""- SINCE BUILD 14: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK""",
     """- PLAYER 2'S OWN GEAR (since build 15). The pause menu belongs to the player who opened it. When PLAYER 2
  presses START, "Items", then "Sora" shows HIS armour and accessories, and what he puts on or takes off there
  is his alone. When player 1 presses START it shows player 1's. Both take from the one common bag. Each hero
  gets the Strength, Defense, AP and the other numbers of his own things, in every room and after a load.
  STILL COMMON: the Keyblade, the abilities and the items in the item places. A change of these in either menu
  is for both heroes.
  IN A SAVE FROM AN OLDER BUILD player 2 has nothing on at first (before build 15 he had the same bonuses as
  player 1). Give him something from the bag.
  Small things: player 2's AP comes from his own accessories while the abilities are the common ones, so his
  menu can show more AP in use than he has. A shop marks player 1's things as "equipped". While a menu is
  open either controller can move in it, as before.
- SINCE BUILD 14: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK"""),
])
print("package tooling and read-me are build 15 (disc v5, patches merged-v9 / merged-v9-own)")
