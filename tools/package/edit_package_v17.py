"""One-off: the test package goes to BUILD 17 (eighth round: a hero or a vehicle of his own for player 2 in the
three small games that had one hero for both: the carpet escape, the sidecar, the toy cannon; plan rows 36 / 37).
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v11-own (own
screens) and patches/merged-v11 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v11 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake` and `tools/own/make_own.py patches/merged-v11-own --base merged-v11 --cannon1view`.
Build 16's patches/merged-v10 / merged-v10-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v17.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 17" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 17")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v11", "merged-v11-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v10-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v11-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v10) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v11) + the same group"),
    ('make("patches/merged-v10-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v11-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v10-own, tools/own/make_own.py --base merged-v10)")',
     '     "OWN SCREENS build (patches/merged-v11-own, tools/own/make_own.py --base merged-v11 --cannon1view)")'),
    ('make("patches/merged-v10/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v11/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v10-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v11-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v10" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v11" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v10-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v11-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v10 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v11 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 16 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 17 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 16 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 17 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.""",
     """NEW IN BUILD 17 (the disc file is still the same): THE THREE SMALL GAMES THAT HAD ONE HERO FOR BOTH PLAYERS
NOW HAVE ONE FOR EACH: in the carpet escape from the ruins player 2 flies his own hero on his own carpet; on
the sidecar near the end player 2 has his own machine; at the toy cannon (Gift Wrapping) player 2 has his own
cannon. Read "THE THREE SMALL GAMES" further down.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter."""),
    ("""- NEW IN BUILD 12: WHEN PLAYER 2 HAS NO HERO, HIS CONTROLLER DRIVES PLAYER 1'S. Three small games have room
  for one hero only: the carpet escape from the ruins, the toy cannon (Gift Wrapping) and the sidecar near
  the end. There both controllers steer and shoot the one hero or cannon, and both screens show the same
  picture. The title menu and other screens without a hero listen to either controller too.""",
     """- THE THREE SMALL GAMES (since build 17). The carpet escape from the ruins, the toy cannon (Gift Wrapping) and
  the sidecar near the end were made for one hero; from build 12 to 16 both controllers drove that one hero.
  NOW PLAYER 2 HAS HIS OWN: the game makes a second hero (or cannon) beside the first when the small game
  begins.
  The carpet escape: two heroes, each on his own carpet, each with his own HP; when one falls the other can
  help him up, as in a fight. The sidecar: two machines, each with its own "Attack / Laser / Drain" buttons
  and its own HP; a Game Over and "Continue" bring both back. The toy cannon: two cannons side by side, each
  turned and fired by its own controller; there BOTH SCREENS SHOW THE SAME PICTURE (the cannons from behind),
  the score and the toy count are for both, and "Reload" loads both.
  Tested by scripts (the escape flown to its end; the sidecar through a Game Over and "Continue"); the end of
  the toy cannon's game was not reached by a script. Not yet played by two people.
- The title menu and other screens without a hero listen to either controller, as since build 12."""),
])
print("package tooling and read-me are build 17 (disc v5, patches merged-v11 / merged-v11-own)")
