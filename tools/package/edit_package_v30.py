"""One-off: the test package goes to BUILD 30 = build 29 + the eighty-third glue --lcrevive (docs/STATE.md part 146: a destroyed
Light Cycle comes back after about 5 seconds while the other rider is still riding). patches/merged-v22 = merge_v7.py with build 29's
options + --lcrevive, merged-v22-own = make_own.py --base merged-v22 --cannon2view. The disc file, the emulator (builds/card1) and the
launcher do not change. Also two read-me corrections: the Light Cycle paragraph of build 12 and the stale "known problem" about the
whirlwinds (part 145: since build 21 every whirlwind ride is a shared move of both heroes).
  python -I tools/package/edit_package_v30.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW30 = """NEW IN BUILD 30 (the disc file, the emulator and the launcher are the same as in build 29), one change in the patch file:
(1) A DESTROYED LIGHT CYCLE COMES BACK (Space Paranoids). Until build 29 the ride was over (Game Over or "mission failed") as
    soon as EITHER cycle was destroyed. Now a destroyed cycle crashes and stays down for about 5 seconds, then it gets up
    again with full HP and rides on, while the other player keeps riding. The ride is over only when BOTH cycles are down
    at the same moment (then Game Over / Continue as before). With one hero nothing changes.
    Tested on one PC: player 2's cycle destroyed and back after 5 seconds (then it steers and attacks), player 1's the
    same, four comebacks in one ride, both destroyed together (Game Over, Continue brings both back); never out of sync.
(2) The read-me's notes about the whirlwinds are corrected: since build 21 a whirlwind always lifts BOTH heroes together
    (one game script moves both), so either player's Cross throws both off. That is how it is meant to work now.
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


if "TEST BUILD 30" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 30")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v22", "merged-v22-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v21-own) + the official widescreen group", "(patches/merged-v22-own) + the official widescreen group"),
    ("(patches/merged-v21) + the same group", "(patches/merged-v22) + the same group"),
    ('make("patches/merged-v21-own/" + NAME,', 'make("patches/merged-v22-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v21-own, tools/own/make_own.py --base merged-v21 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v22-own, tools/own/make_own.py --base merged-v22 --cannon2view)")'),
    ('make("patches/merged-v21/" + NAME,', 'make("patches/merged-v22/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v21-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v22-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v21" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v22" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v21-own lines", "does not start with exactly the merged-v22-own lines"),
    ("does not start with exactly the merged-v21 lines", "does not start with exactly the merged-v22 lines"),
])
edit(START, [
    ("   BUILDS 13 TO 29 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 30 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 29 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 30 (OWN SCREENS)"),
    ("NEW IN BUILD 29 (the disc file, the emulator and the launcher are the same as in build 28), one change in the patch file:\n",
     NEW30 + "NEW IN BUILD 29 (the disc file, the emulator and the launcher are the same as in build 28), one change in the patch file:\n"),
    ("  lost when EITHER ship is destroyed (the same rule as on the Light Cycles). There is still one hull gauge: it\n",
     "  lost when EITHER ship is destroyed (on the Light Cycles that was so until build 29). There is still one hull gauge: it\n"),
    ("  pose with nothing under him). One thing to know: on the Light Cycle the ride is over when EITHER cycle is\n"
     "  destroyed, as the game does it for one rider; nobody can be picked up there.\n",
     "  pose with nothing under him). On the Light Cycle a destroyed cycle comes back after about 5 seconds (since\n"
     "  build 30; before, the ride was over when EITHER cycle was destroyed); the ride is over when both are down.\n"),
    ("- Some small games listen for a button on EITHER controller where the game means \"the rider\" (the whirlwinds\n"
     "  in the Land of Dragons, for example): a press by one player can count for the other's ride.\n",
     "- The whirlwinds (Land of Dragons, the Storm Rider fight) always lift BOTH heroes together (a shared move since\n"
     "  build 21: one game script moves both), so either player's Cross throws both off. Meant so.\n"),
])
