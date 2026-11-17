"""One-off: the test package goes to BUILD 19 = build 18 + the sixty-first glue (--itemsync): player 2's "Items" list
shows the item places as they are (docs/STATE.md, Eighth round, part 85; the fault was in every build since 15).
Builds 17 and 18 were never given out; for the user build 19 is the build after 16, so the read-me's "NEW IN
BUILD 18" becomes "NEW IN BUILD 19" with a fourth point.
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v13-own (own
screens) and patches/merged-v13 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v13 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync` and
`tools/own/make_own.py patches/merged-v13-own --base merged-v13 --cannon1view`.
Build 18's patches/merged-v12 / merged-v12-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v19.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 19" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 19")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v13", "merged-v13-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v12-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v13-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v12) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v13) + the same group"),
    ('make("patches/merged-v12-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v13-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v12-own, tools/own/make_own.py --base merged-v12 --cannon1view)")',
     '     "OWN SCREENS build (patches/merged-v13-own, tools/own/make_own.py --base merged-v13 --cannon1view)")'),
    ('make("patches/merged-v12/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v13/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v12-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v13-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v12" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v13" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v12-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v13-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v12 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v13 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 18 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 19 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("NEW IN BUILD 18 (the disc file is still the same), three things:",
     "NEW IN BUILD 19 (the disc file is still the same), four things:"),
    ("""    (builds 12 to 16); now he is let go after a minute. Read "BOSSES THAT HOLD A HERO" further down.""",
     """    (builds 12 to 16); now he is let go after a minute. Read "BOSSES THAT HOLD A HERO" further down.
(4) PLAYER 2'S "ITEMS" LIST IS RIGHT AGAIN. In builds 15 and 16 his list could still show an item that had
    already been used, and let him take it. Read "PLAYER 2'S OWN GEAR" further down."""),
    ("  player has his own armour and accessories (since build 15) and switches his own abilities (since build 18).",
     "  player has his own armour and accessories (since build 15) and switches his own abilities (since build 19)."),
    ("- THE THREE SMALL GAMES (since build 18). The carpet escape from the ruins, the toy cannon (Gift Wrapping) and",
     "- THE THREE SMALL GAMES (since build 19). The carpet escape from the ruins, the toy cannon (Gift Wrapping) and"),
    ("""  SINCE BUILD 18 THE ABILITIES' SWITCHES ARE HIS OWN TOO.""",
     """  SINCE BUILD 19 THE ABILITIES' SWITCHES ARE HIS OWN TOO."""),
    ("""  STILL COMMON: the Keyblade, the items in the item places, the list of abilities learned, the Drive Forms'
  own abilities. A change of these in either menu is for both heroes.""",
     """  STILL COMMON: the Keyblade, the items in the item places, the list of abilities learned, the Drive Forms'
  own abilities. A change of these in either menu is for both heroes. THE ITEMS IN THE ITEM PLACES ARE ONE SET
  FOR BOTH: a Potion either player uses is gone for both, and each player's "Items" list shows what is left.
  (In builds 15 and 16 player 2's list kept showing an item that was gone; cured in build 19.)"""),
    ("- BOSSES THAT HOLD A HERO (since build 18).", "- BOSSES THAT HOLD A HERO (since build 19)."),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 18 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 19 (OWN SCREENS)"),
])
print("package tooling and read-me are build 19 (disc v5, patches merged-v13 / merged-v13-own)")
