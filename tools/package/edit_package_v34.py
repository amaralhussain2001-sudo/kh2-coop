"""One-off: the test package goes to BUILD 34 = build 33 + the own-screen step 10 --partnerdrive (docs/STATE.md part 150: each
player sees the partner's DRIVE / FORM strip beside the partner's small gauge). patches/merged-v26 = merge_v7.py with build 33's
options (the same words as merged-v25), merged-v26-own = make_own.py --base merged-v26 --cannon2view --partnerdrive. The disc file,
the emulator (builds/card1) and the launcher do not change.
  python -I tools/package/edit_package_v34.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"

NEW34 = """NEW IN BUILD 34 (the disc file, the emulator and the launcher are the same as in build 33), one change in the patch file:
(1) YOU SEE YOUR PARTNER'S DRIVE GAUGE. Next to your partner's small round gauge (top right) there is now his DRIVE
    strip too: the bars, MAX and the number, exactly as on his own screen. When he is in a Drive Form it shows his
    FORM countdown instead, so you can see how long his form lasts. Your own gauge (bottom right) is as before. Where
    the game hides the Drive gauge (in a town), the partner's strip keeps the game's own "hidden" too (built so, not
    tried in a town yet).
    Tested on one PC: a fight in Agrabah (with Donald/Goofy gauges) and a room without them: the strip sits beside the
    partner's gauge in both; player 2 in Valor Form: player 1 sees his FORM countdown, player 2 sees player 1's DRIVE
    strip; never out of sync.
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


if "TEST BUILD 34" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 34")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v26", "merged-v26-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v25-own) + the official widescreen group", "(patches/merged-v26-own) + the official widescreen group"),
    ("(patches/merged-v25) + the same group", "(patches/merged-v26) + the same group"),
    ('make("patches/merged-v25-own/" + NAME,', 'make("patches/merged-v26-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v25-own, tools/own/make_own.py --base merged-v25 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v26-own, tools/own/make_own.py --base merged-v26 --cannon2view --partnerdrive)")'),
    ('make("patches/merged-v25/" + NAME,', 'make("patches/merged-v26/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v25-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v26-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v25" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v26" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v25-own lines", "does not start with exactly the merged-v26-own lines"),
    ("does not start with exactly the merged-v25 lines", "does not start with exactly the merged-v26 lines"),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 33 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 34 (OWN SCREENS)"),
    ("NEW IN BUILD 33 (the disc file, the emulator and the launcher are the same as in build 32), one change in the patch file:\n",
     NEW34 + "NEW IN BUILD 33 (the disc file, the emulator and the launcher are the same as in build 32), one change in the patch file:\n"),
])
