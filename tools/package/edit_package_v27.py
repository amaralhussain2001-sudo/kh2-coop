"""One-off: the test package goes to BUILD 27 = build 26 + the seventy-ninth glue --menuowner (docs/STATE.md part 141: the player
who opens a screen alone controls it). patches/merged-v19 = test-v29-mo3 (merge_v7.py with build 24's options + --menuowner),
patches/merged-v19-own = test-own-mo3 (make_own.py --base test-v29-mo3 --cannon2view; the same lines as --base merged-v19).
The disc file and the emulator (builds/card1) do not change.
Edits: make_package_patch.py, make_test_package.py, the kit's read-me and two-PC start text.
  python -I tools/package/edit_package_v27.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW27 = """NEW IN BUILD 27 (the disc file and the emulator are the same as in build 26), one change in the patch file:
(1) WHO OPENS A SCREEN CONTROLS IT. Up to build 26 both controllers worked in every menu, shop and talk, so the other
    player's buttons could move your cursor, buy, or close your shop. Now:
    - THE PAUSE MENU belongs to the player who pressed START: only his buttons move and choose in it (and its pages).
    - A SHOP, THE MOOGLE, A SAVE POINT (and the world map after it), A TALK WITH ITS CHOICES ("Yes / No", "Make
      presents? / Let's make it!"), and the rules screen of a small game started there belong to the player who
      pressed Triangle (the green command). Only his buttons work there until it is over.
    - EVERYTHING NOBODY OPENED is still for both: story scenes and their text, tutorial boxes, Game Over / Continue,
      Retry / Quit, the title screen, the Gummi Ship's menus, boss button-mashing. Walking and fighting are as before.
    There is no time limit: the other player waits until the owner has finished.
    Tested on one PC (each also against build 26): player 1 opens the pause menu, player 2's Down does nothing, player
    1's Down works; the same the other way round; player 2 buys a Potion while player 1 presses Cross (in build 26
    player 1's Cross closed player 2's shop; now the Potion is bought); player 2 talks to the elf and player 1 presses
    Up in "Make presents?" (in build 26 the hand jumped to "Hold on."; now player 2's "Let's make it!" starts the game).
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


if "TEST BUILD 27" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 27")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v19", "merged-v19-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v18-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v19-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v18) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v19) + the same group"),
    ('make("patches/merged-v18-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v19-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v18-own, tools/own/make_own.py --base merged-v18 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v19-own, tools/own/make_own.py --base merged-v19 --cannon2view)")'),
    ('make("patches/merged-v18/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v19/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v18-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v19-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v18" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v19" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v18-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v19-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v18 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v19 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 26 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 27 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 26 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 27 (OWN SCREENS)"),
    ("NEW IN BUILD 26 (the disc file and the patch files are the same as in build 24), one change in the emulator program:\n",
     NEW27 + "NEW IN BUILD 26 (the disc file and the patch files are the same as in build 24), one change in the emulator program:\n"),
])
