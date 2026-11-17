"""One-off: the test package goes to BUILD 14 (eighth round). THE DISC FILE IS STILL "TEST v5" (builds 12 and 13);
only the patch files change: the package now takes patches/merged-v8-own (own screens) and patches/merged-v8
(shared-screen fallback), written by `tools/merge/merge_v7.py patches/merged-v8` (glues 30 to 45 and 47) and
`tools/own/make_own.py patches/merged-v8-own --base merged-v8`. Build 13's patches/merged-v7 / merged-v7-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v14.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 14" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 14")     # (the read-me is the LAST file edited: the guard holds only after a full run)

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v7-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v8-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v7) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v8) + the same group"),
    ('make("patches/merged-v7-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v8-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v7-own, tools/own/make_own.py --base merged-v7)")',
     '     "OWN SCREENS build (patches/merged-v8-own, tools/own/make_own.py --base merged-v8)")'),
    ('make("patches/merged-v7/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v8/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v7-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v8-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v7" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v8" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v7-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v8-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v7 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v8 lines")'),
])
edit(START, [
    ("""   BUILD 13 KEEPS THAT DISC FILE; only small files changed. Copy the whole folder to the second PC again all the
""", """   BUILDS 13 AND 14 KEEP THAT DISC FILE; only small files changed. Copy the whole folder to the second PC again all the
"""),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 13 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 14 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.""",
     """NEW IN BUILD 14 (the disc file is still the same): a boss's green command (Triangle) is taken by ONE hero. If
both players press it at the same moment, the first one gets the move and the other's press does nothing.
This cures Xigbar's sniper part (it never ended when both pressed "Warp Snipe") and Luxord's card trick (a
hero stayed held for the whole fight).
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter."""),
    ("""- BUILD 13, KNOWN AND NOT SOLVED: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK (both in The World That Never
  Was) do not work right with two heroes: a hero can stay held for the rest of the fight. It was so in build
  12 too (there Xigbar's fight could even stop the game). SAVE BEFORE these two fights and tell me what you saw.
""", """- SINCE BUILD 14: XIGBAR'S SNIPER PART and LUXORD'S CARD TRICK (both in The World That Never Was) work with two
  heroes in the tests: the hero who presses the green command first does the move, the other stays free. In
  builds 12 and 13 a hero could stay held for the rest of the fight when both pressed at once. A test script
  cannot judge Luxord's card game itself, so SAVE BEFORE these two fights and tell me what you saw.
  While a boss holds one hero in such a move, the OTHER player's Triangle on that boss does nothing. That is
  on purpose.
"""),
])
print("package tooling and read-me are build 14 (disc v5, patches merged-v8 / merged-v8-own)")
