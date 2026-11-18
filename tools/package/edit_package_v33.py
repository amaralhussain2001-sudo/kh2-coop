"""One-off: the test package goes to BUILD 33 = build 32 + the eighty-fifth glue's area part --sound2area (docs/STATE.md part 149:
the AREA sounds - the two Hollow Bastion rooms hb23 and hb25 are the only rooms with them - also come from the nearer camera).
patches/merged-v25 = merge_v7.py with build 32's options + --sound2area, merged-v25-own = make_own.py --base merged-v25
--cannon2view. The disc file, the emulator (builds/card1) and the launcher do not change.
  python -I tools/package/edit_package_v33.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"

NEW33 = """NEW IN BUILD 33 (the disc file, the emulator and the launcher are the same as in build 32), one change in the patch file:
(1) THE AREA SOUNDS FOLLOW THE NEARER HERO TOO. A few sounds belong to a whole area instead of one spot (in the
    whole game only two rooms of Hollow Bastion have them). Until build 32 their spot was taken from player 1's
    camera; now each such sound comes from the spot nearest to whichever camera is closer, so it is as loud as it
    should be for the player standing near it. With build 32's change every sound in the game now follows the
    nearer hero.
    Tested on one PC in both rooms: player 1 standing, player 2 far away: 58 area sounds louder for player 2, none
    quieter than in build 32; the other sounds as in build 32; never out of sync.
"""


def edit(path, pairs):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8-sig").replace("\r\n", "\n")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) >= 1:      # this pair is already in (a first run stopped half way)
            continue
        assert t.count(old) == 1, (str(path), t.count(old), old[:70])
        t = t.replace(old, new)
    out = t.replace("\n", "\r\n") if crlf else t
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    print("edited", path)


if "TEST BUILD 33" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 33")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v25", "merged-v25-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v24-own) + the official widescreen group", "(patches/merged-v25-own) + the official widescreen group"),
    ("(patches/merged-v24) + the same group", "(patches/merged-v25) + the same group"),
    ('make("patches/merged-v24-own/" + NAME,', 'make("patches/merged-v25-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v24-own, tools/own/make_own.py --base merged-v24 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v25-own, tools/own/make_own.py --base merged-v25 --cannon2view)")'),
    ('make("patches/merged-v24/" + NAME,', 'make("patches/merged-v25/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v24-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v25-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v24" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v25" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v24-own lines", "does not start with exactly the merged-v25-own lines"),
    ("does not start with exactly the merged-v24 lines", "does not start with exactly the merged-v25 lines"),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 32 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 33 (OWN SCREENS)"),
    ("NEW IN BUILD 32 (the disc file, the emulator and the launcher are the same as in build 31), one change in the patch file:\n",
     NEW33 + "NEW IN BUILD 32 (the disc file, the emulator and the launcher are the same as in build 31), one change in the patch file:\n"),
    ("    belong to a whole area (a river, a waterfall) are only partly better for now (their spot is still chosen from\n"
     "    player 1's camera).\n",
     "    belong to a whole area were only partly better in build 32; build 33 does them too.\n"),
])
