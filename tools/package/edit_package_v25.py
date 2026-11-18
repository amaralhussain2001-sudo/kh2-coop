"""One-off: the test package goes to BUILD 25 = build 24 + the emulator build emulator-src/builds/pace1 (docs/STATE.md part 139: the
frame pacing fix; the user's words "update ... to the new batch"). The disc file and the patch files do not change.
Edits: make_test_package.py (VIEW_EXE -> builds/pace1), the read-me and the two-PC start text of the kit, and the same two texts in
the user's Desktop folder PS2-ONLINE-KH2-TEST-b24 (which already holds the pace1 exe from the build 25 update zip).
  python -I tools/package/edit_package_v25.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"
DESK = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2-TEST-b24")

NEW25 = """NEW IN BUILD 25 (the disc file and the patch files are the same as in build 24), one change in the emulator program
(emulator\\pcsx2-qtx64.exe):
(1) SMOOTHER FRAME RATE ONLINE. When one PC is a little slower than the other (or the internet is uneven), the faster PC
    had to wait for it many times a second and then ran fast to win the time back, so the frame rate jumped up and down
    (in your first session on two PCs the host waited 55.7 s in 9.5 minutes). Now the faster PC simply follows the slower
    PC's pace. Only the timing on the PC changes; the game is not changed. Tested on one PC with a copy that runs 1 % slow:
    1,488 waits (19.3 s in 100 s) with build 24, 119 waits (0.6 s) with build 25, the same game speed, never out of sync.
    It cannot make the slower PC faster: if one PC cannot hold 60 fps, both players choose the same lower Picture.
    ALSO FOUND: "OUT OF SYNC" right at the start (about 7 seconds in) comes from TWO DIFFERENT MEMORY CARD FILES. The join
    check does not notice a different card yet. Before playing, close the game on both PCs and copy the host's
    emulator\\memcards\\Mcd001.ps2 to the same place on the other PC.
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


README_PAIRS = [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 24 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 25 (OWN SCREENS)"),
    ("NEW IN BUILD 24 (the disc file is still the same), one change:\n", NEW25 + "NEW IN BUILD 24 (the disc file is still the same), one change:\n"),
]
START_PAIRS = [
    ("   BUILDS 13 TO 24 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 25 KEEP THAT DISC FILE; only small files changed."),
]

if "TEST BUILD 25" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 25")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
assert (HERE.parent.parent / "emulator-src" / "builds" / "pace1" / "pcsx2-qtx64.exe").exists()

edit(HERE / "make_test_package.py", [
    ('VIEW_EXE = ROOT / "emulator-src" / "builds" / "view12" / "pcsx2-qtx64.exe"   # own-view emulator build',
     'VIEW_EXE = ROOT / "emulator-src" / "builds" / "pace1" / "pcsx2-qtx64.exe"    # own-view build + frame pacing (build 25)'),
])
edit(DESK / "START-HERE (TWO PCs AT HOME).txt", START_PAIRS)
edit(DESK / "1-READ-ME-FIRST (KH2 TEST).txt", README_PAIRS)
edit(START, START_PAIRS)
edit(README, README_PAIRS)
