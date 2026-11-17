"""One-off: the test package goes to BUILD 23 = build 22 + ONE FIX (docs/STATE.md, Tenth round, part 130): glue 66's
shots' table (the Gummi flight's "which ship fired this shot" byte per cannon shot) moved from 0x000EE800 to 0x000DF000.
Build 22 had placed glues 72 to 75 inside that table, so a cannon shot could change one byte of their code until the next
frame (tools/merge/edit_merge_v7_gqtable.py; patches/merged-v17 differs from merged-v16 in exactly two words).
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v17-own (own screens)
and patches/merged-v17 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v17 <build 22's options>` and
`tools/own/make_own.py patches/merged-v17-own --base merged-v17 --cannon2view`. Build 22's merged-v16 / merged-v16-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v23.py          (run ONCE; it refuses a second run)
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


if "TEST BUILD 23" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 23")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v17", "merged-v17-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v16-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v17-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v16) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v17) + the same group"),
    ('make("patches/merged-v16-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v17-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v16-own, tools/own/make_own.py --base merged-v16 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v17-own, tools/own/make_own.py --base merged-v17 --cannon2view)")'),
    ('make("patches/merged-v16/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v17/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v16-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v17-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v16" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v17" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v16-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v17-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v16 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v17 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 22 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 23 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""NEW IN BUILD 22 (the disc file is still the same), five things:""",
     """NEW IN BUILD 23 (the disc file is still the same), one fix:
(1) THE GUMMI SHIP: the note "which ship fired this shot" (it splits the points between the two ships) was kept in
    the same memory as four of build 22's new parts (the Drive save, the Potion target choice, picking up drops,
    the form after a door). A cannon shot could change one byte of them for a moment. The note has its own place
    now. Tested: the Gummi flight with only player 1 firing, only player 2, both: the same points as build 22,
    each ship's points to its own player, no fault. Nothing else changed.
    ALSO TESTED NOW, NOTHING TO CHANGE: Load Game FROM THE TITLE SCREEN gives player 2 his own saved Drive gauge
    (build 22 too); a Drive Form through five doors in a row stays right for player 1 and player 2.
NEW IN BUILD 22 (the disc file is still the same), five things:"""),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 22 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 23 (OWN SCREENS)"),
])
print("package tooling and read-me are build 23 (disc v5, patches merged-v17 / merged-v17-own)")
