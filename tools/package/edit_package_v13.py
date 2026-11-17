"""One-off: the test package goes to BUILD 13 (eighth round). THE DISC FILE IS THE SAME AS IN BUILD 12 ("TEST v5");
only the patch files change: the package now takes patches/merged-v7-own (own screens) and patches/merged-v7
(shared-screen fallback), written by tools/merge/merge_v7.py and tools/own/make_own.py --base merged-v7.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v13.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 13" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 13")     # (the read-me is the LAST file edited: the guard holds only after a full run)

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v6-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v7-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v6) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v7) + the same group"),
    ('make("patches/merged-v6-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v7-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v6-own, tools/own/make_own.py)")',
     '     "OWN SCREENS build (patches/merged-v7-own, tools/own/make_own.py --base merged-v7)")'),
    ('make("patches/merged-v6/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v7/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v6-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v7-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v6" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v7" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v6-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v7-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v6 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v7 lines")'),
])
edit(START, [
    ("""   BUILD 12 HAS A NEW DISC FILE ("TEST v5"). Delete the old folder on the second PC and copy this one.
""", """   BUILD 12 HAS A NEW DISC FILE ("TEST v5"). Delete the old folder on the second PC and copy this one.
   BUILD 13 KEEPS THAT DISC FILE; only small files changed. Copy the whole folder to the second PC again all the
   same (it is the sure way: both PCs must have exactly the same patch files).
"""),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 12 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 13 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.""",
     """NEW IN BUILD 13 (the disc file is the same as in build 12): BOTH heroes can be in a Drive Form at the same time;
when both heroes fall and King Mickey comes, EACH player plays a King Mickey; a boss's clash takes the hero who
is fighting and its green command is in that player's menu; enemy groups also wake up for player 2; changing
the Keyblade in the menu no longer stops the game.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter."""),
])
print("package tooling and read-me are build 13 (disc v5, patches merged-v7 / merged-v7-own)")
