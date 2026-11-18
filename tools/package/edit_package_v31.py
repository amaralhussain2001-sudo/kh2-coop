"""One-off: the test package goes to BUILD 31 = build 30 + the eighty-fourth glue --partnerview (docs/STATE.md part 147: hold L2 and
press START = the pause menu on the partner's gear, read-only). patches/merged-v23 = merge_v7.py with build 30's options +
--partnerview, merged-v23-own = make_own.py --base merged-v23 --cannon2view. The disc file, the emulator (builds/card1) and the
launcher do not change.
  python -I tools/package/edit_package_v31.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW31 = """NEW IN BUILD 31 (the disc file, the emulator and the launcher are the same as in build 30), one change in the patch file:
(1) LOOK AT YOUR PARTNER'S GEAR: HOLD L2 AND PRESS START. The pause menu then opens on the OTHER player's things: his
    Keyblade, armour, accessories, abilities, items, his munny and his bag, exactly as his own menu shows them. It is only
    for looking: equipping, switching abilities, using an item, the refill switch and the Customize settings do nothing
    there, and when the menu closes everything is put back as it was. START without L2 opens your own menu as before.
    Tested on one PC: player 1 holding L2 + START sees player 2's accessory, player 2 holding L2 + START sees player 1's,
    both menus close with every byte as before, the world stays paused meanwhile, START alone still opens each player's
    own menu as in build 30; never out of sync. Not tried yet: pressing "equip" inside the partner view (the test save
    had nothing that can be switched); the code blocks it.
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


if "TEST BUILD 31" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 31")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v23", "merged-v23-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v22-own) + the official widescreen group", "(patches/merged-v23-own) + the official widescreen group"),
    ("(patches/merged-v22) + the same group", "(patches/merged-v23) + the same group"),
    ('make("patches/merged-v22-own/" + NAME,', 'make("patches/merged-v23-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v22-own, tools/own/make_own.py --base merged-v22 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v23-own, tools/own/make_own.py --base merged-v23 --cannon2view)")'),
    ('make("patches/merged-v22/" + NAME,', 'make("patches/merged-v23/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v22-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v23-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v22" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v23" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v22-own lines", "does not start with exactly the merged-v23-own lines"),
    ("does not start with exactly the merged-v22 lines", "does not start with exactly the merged-v23 lines"),
])
edit(START, [
    ("   BUILDS 13 TO 30 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 31 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 30 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 31 (OWN SCREENS)"),
    ("NEW IN BUILD 30 (the disc file, the emulator and the launcher are the same as in build 29), one change in the patch file:\n",
     NEW31 + "NEW IN BUILD 30 (the disc file, the emulator and the launcher are the same as in build 29), one change in the patch file:\n"),
])
