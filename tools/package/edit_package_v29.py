"""One-off: the test package goes to BUILD 29 = build 28 + the eighty-first glue --sumscene2 (docs/STATE.md part 144: player 2's
Summon plays its entrance movie like player 1's). patches/merged-v21 = merge_v7.py with build 28's options + --sumscene2,
merged-v21-own = make_own.py --base merged-v21 --cannon2view. The disc file, the emulator (builds/card1) and the launcher do not change.
Edits: make_package_patch.py and make_test_package.py v20 -> v21; the kit's read-me (NEW IN BUILD 29, the build 10 paragraph) and
the two-PC start text (13 TO 29).
  python -I tools/package/edit_package_v29.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW29 = """NEW IN BUILD 29 (the disc file, the emulator and the launcher are the same as in build 28), one change in the patch file:
(1) PLAYER 2'S SUMMON PLAYS ITS ENTRANCE MOVIE TOO. Until build 28 only player 1's Summon had the movie; when player 2 called,
    the friend just appeared. Now the movie plays for either player, with the hero who called (both screens show it, both
    players wait for it, as for player 1's). The game's own Config choice "Summon Effects" still decides whether the movie
    plays. Tested on one PC: Genie and Peter Pan called by player 2 (the movie, then the friend beside player 2), Dismiss by
    player 2 after the movie, Genie called by player 1 (as before); never out of sync.
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


if "TEST BUILD 29" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 29")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v21", "merged-v21-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v20-own) + the official widescreen group", "(patches/merged-v21-own) + the official widescreen group"),
    ("(patches/merged-v20) + the same group", "(patches/merged-v21) + the same group"),
    ('make("patches/merged-v20-own/" + NAME,', 'make("patches/merged-v21-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v20-own, tools/own/make_own.py --base merged-v20 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v21-own, tools/own/make_own.py --base merged-v21 --cannon2view)")'),
    ('make("patches/merged-v20/" + NAME,', 'make("patches/merged-v21/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v20-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v21-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v20" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v21" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v20-own lines", "does not start with exactly the merged-v21-own lines"),
    ("does not start with exactly the merged-v20 lines", "does not start with exactly the merged-v21 lines"),
])
edit(START, [
    ("   BUILDS 13 TO 28 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 29 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 28 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 29 (OWN SCREENS)"),
    ("NEW IN BUILD 28 (the disc file and the emulator are the same as in build 27), one change in the patch file and the launcher:\n",
     NEW29 + "NEW IN BUILD 28 (the disc file and the emulator are the same as in build 27), one change in the patch file and the launcher:\n"),
    ("  is grey). When player 1 calls, the game shows its entrance movie on player 1's screen and both players wait\n"
     "  for it. When player 2 calls there is no movie: the friend just appears. Tried with all four (Chicken Little,\n"
     "  Genie, Stitch, Peter Pan).\n",
     "  is grey). The game shows its entrance movie and both players wait for it. (Until build 28 only player 1's\n"
     "  call had the movie; since build 29 player 2's has it too.) Tried with all four (Chicken Little, Genie,\n"
     "  Stitch, Peter Pan).\n"),
])
