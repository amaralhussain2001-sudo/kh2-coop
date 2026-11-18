"""One-off: the test package goes to BUILD 35 = build 34 + the eighty-sixth glue --hullgauges (docs/STATE.md part 152: in a Gummi
flight both ships' hull gauges are on screen, ship 1's at the game's place, ship 2's at the bottom left). patches/merged-v27 =
merge_v7.py with build 34's options + --hullgauges, merged-v27-own = make_own.py --base merged-v27 --cannon2view --partnerdrive.
Also the read-me lines of build 34 / 31 that said "not tried yet" are brought up to date (part 151). The disc file, the emulator
(builds/card1) and the launcher do not change.
  python -I tools/package/edit_package_v35.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"

NEW35 = """NEW IN BUILD 35 (the disc file, the emulator and the launcher are the same as in build 34), one change in the patch file:
(1) BOTH GUMMI SHIPS HAVE THEIR OWN HULL GAUGE. In a Gummi Ship flight the round hull gauge at the bottom right is now
    always player 1's ship (the small "1" beside it), and player 2's ship has the same gauge at the bottom LEFT (with a
    "2"). Until build 34 there was one gauge that showed whichever ship was weaker.
    Tested on one PC: Gummi route 8 played through with both gauges on screen: the same points at every check as
    build 34 and the same end (90,939); a flight where ship 1 was hit hard and ship 2 hardly: gauge 1 nearly empty,
    gauge 2 full; Game Over and the retry: both gauges come back; never out of sync.
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

if "TEST BUILD 35" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 35")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v27", "merged-v27-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v26-own) + the official widescreen group", "(patches/merged-v27-own) + the official widescreen group"),
    ("(patches/merged-v26) + the same group", "(patches/merged-v27) + the same group"),
    ('make("patches/merged-v26-own/" + NAME,', 'make("patches/merged-v27-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v26-own, tools/own/make_own.py --base merged-v26 --cannon2view --partnerdrive)")',
     '"OWN SCREENS build (patches/merged-v27-own, tools/own/make_own.py --base merged-v27 --cannon2view --partnerdrive)")'),
    ('make("patches/merged-v26/" + NAME,', 'make("patches/merged-v27/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v26-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v27-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v26" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v27" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v26-own lines", "does not start with exactly the merged-v27-own lines"),
    ("does not start with exactly the merged-v26 lines", "does not start with exactly the merged-v27 lines"),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 34 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 35 (OWN SCREENS)"),
    ("NEW IN BUILD 34 (the disc file, the emulator and the launcher are the same as in build 33), one change in the patch file:\n",
     NEW35 + "NEW IN BUILD 34 (the disc file, the emulator and the launcher are the same as in build 33), one change in the patch file:\n"),
    ("the partner's strip keeps the game's own \"hidden\" too (built so, not\n    tried in a town yet).\n",
     "the partner's strip keeps the game's own \"hidden\" too (tried later: in\n    the first town of a New Game neither PC shows a strip).\n"),
    ("Not tried yet: pressing \"equip\" inside the partner view (the test save\n    had nothing that can be switched); the code blocks it.\n",
     "Tried later: taking an ability off inside the partner view does nothing\n    (\"Don't Equip\" chosen, the ability stays on); in your own menu the same buttons take it off.\n"),
])
