"""One-off: the test package goes to BUILD 26 = build 25 + the emulator build emulator-src/builds/card1 (docs/STATE.md part 140:
the host's memory card travels to a friend whose card differs; the card check of the join works again; protocol 5).
The disc file and the patch files do not change. Edits: make_test_package.py (VIEW_EXE -> builds/card1), the read-me and the
two-PC start text of the kit. (The user's Desktop folder is brought to build 26 by make_b26_update.py, not here.)
  python -I tools/package/edit_package_v26.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW26 = """NEW IN BUILD 26 (the disc file and the patch files are the same as in build 24), one change in the emulator program:
(1) THE MEMORY CARD TRAVELS WITH THE GAME. When the friend joins and his memory card is not the same as the host's, the
    host's card is sent to him before the game starts (usually in under a second; his screen says "receiving the host's
    card ... %"). His own card is kept as a backup in emulator\\memcards (Mcd001-backup-<date>.ps2) and he plays with the
    host's card, so the saves of your games together end up on both PCs. No more copying the card by hand, and no more
    "OUT OF SYNC" a few seconds after the start because of two different cards. The card check of the join works again
    (before build 26 it never noticed a different card).
    WHOEVER HOSTS DECIDES THE CARD: host on the PC that has your saves.
    Both PCs need build 26: a PC with build 25 or older is refused ("Different version of the online emulator").
    Tested on one PC: two different cards (the friend's card became byte for byte the host's, his backup byte for byte
    his old card, never out of sync), the same cards (nothing sent, no backup), 20 % of the packets lost (the card still
    arrived in about half a second), and a whole start through both launchers and the connection helper.
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
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 25 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 26 (OWN SCREENS)"),
    ("NEW IN BUILD 25 (the disc file and the patch files are the same as in build 24), one change in the emulator program\n",
     NEW26 + "NEW IN BUILD 25 (the disc file and the patch files are the same as in build 24), one change in the emulator program\n"),
]
START_PAIRS = [
    ("   BUILDS 13 TO 25 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 26 KEEP THAT DISC FILE; only small files changed."),
]

if "TEST BUILD 26" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 26")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
assert (HERE.parent.parent / "emulator-src" / "builds" / "card1" / "pcsx2-qtx64.exe").exists()

edit(HERE / "make_test_package.py", [
    ('VIEW_EXE = ROOT / "emulator-src" / "builds" / "pace1" / "pcsx2-qtx64.exe"    # own-view build + frame pacing (build 25)',
     'VIEW_EXE = ROOT / "emulator-src" / "builds" / "card1" / "pcsx2-qtx64.exe"    # own view + pacing + card transfer (build 26)'),
])
edit(START, START_PAIRS)
edit(README, README_PAIRS)
