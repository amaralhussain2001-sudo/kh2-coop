"""One-off: the test package goes to BUILD 6 with a NEW DISC FILE (TEST v3 = v2 + Mail Delivery for two):
package builder, rehearsal copies, the disc-maker script and the read-me files."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
V3_SHA = "23504a4bacc419144d68578192b8848519eda3ec"


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path.name, t.count(old), old[:60])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


if "TEST v3" in (HERE / "make_test_package.py").read_text(encoding="utf-8"):
    raise SystemExit("already v3")

edit(HERE / "make_test_package.py", [
    ("(kh2-coop-v2.iso, unchanged since TEST v2).", "(kh2-coop-v3.iso = v2 + Mail Delivery for two, since TEST build 6)."),
    ('DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v2.kh2patch"', 'DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v3.kh2patch"'),
    ('DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v2).iso"', 'DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"'),
])
edit(HERE / "make_rehearsal_copies.py", [
    ("(local/iso/kh2-coop-v2.iso)", "(local/iso/kh2-coop-v3.iso)"),
    ('DISC = ROOT / "local" / "iso" / "kh2-coop-v2.iso"', 'DISC = ROOT / "local" / "iso" / "kh2-coop-v3.iso"'),
    ('DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v2).iso"', 'DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"'),
])
edit(HERE / "kit" / "MAKE-KH2-DISC" / "Make-KH2-Disc.ps1", [
    ('$PatchFile = Join-Path $Here "kh2-coop-v2.kh2patch"', '$PatchFile = Join-Path $Here "kh2-coop-v3.kh2patch"'),
    ('$OutName = "Kingdom Hearts II - Final Mix (2 Players TEST v2).iso"', '$OutName = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"'),
    ('Fail "The file kh2-coop-v2.kh2patch is missing', 'Fail "The file kh2-coop-v3.kh2patch is missing'),
])
edit(HERE / "kit" / "HOW-TO-SET-UP (FRIEND).txt", [
    ("""follow it: make the disc file (STEP 1; if you made the
   "TEST v2" file for build 2 already, keep it, it is the same), then start""",
     """follow it: make the NEW disc file (STEP 1; the
   "TEST v2" file of the older builds is not used any more, delete it), then start"""),
])
edit(HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt", [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 5 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 6 (OWN SCREENS)"),
    ("""If you have build 3 or 4: replace the whole test folder with this one (both players). The disc file stays the same.
""", """NEW IN BUILD 6: Mail Delivery for two: each player starts on his own skateboard, with his own board commands.
!! THE DISC FILE CHANGED IN BUILD 6. If you have an older build: replace the whole test folder with this one
   (both players) AND make the new disc file "TEST v3" (STEP 1). Delete the old "TEST v2" file.
"""),
    ("""If you made the "TEST v1" disc file before: it is not used any more. Delete it from this folder's MY-GAMES and
make the v2 file (STEP 1). The two must not sit there together.
""", """If you made the "TEST v1" or "TEST v2" disc file before: they are not used any more. Delete them from this
folder's MY-GAMES and make the v3 file (STEP 1). Only ONE Kingdom Hearts file may sit there.
"""),
    ('"MY-GAMES (never share)":  Kingdom Hearts II - Final Mix (2 Players TEST v2).iso',
     '"MY-GAMES (never share)":  Kingdom Hearts II - Final Mix (2 Players TEST v3).iso'),
    ("       12edc56fdb0baac302c373e554185921242e6533", "       " + V3_SHA),
    ('2. Game: the "2 Players TEST v2" file (the disc file did not change since build 2). Controllers: "2 players, no',
     '2. Game: the "2 Players TEST v3" file (new in build 6). Controllers: "2 players, no'),
    ("""- NEW: the rules screen of a small game (Struggle, the jobs) can be closed by either player.
""", """- NEW: the rules screen of a small game (Struggle, the jobs) can be closed by either player.
- NEW IN BUILD 6: skateboards. In the job Mail Delivery each player starts on his own board and has the board
  commands (Heelflip, Jump) in his own menu. In town each player can hop on a board of his own with Triangle.
"""),
    ("""- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard) and the bag job. If a job cannot be finished, let player 1 do it alone and
  tell me which one it was.
""", """- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: the bag job.
  In Mail Delivery both ride now; handing in letters by player 2 and the end of the job were not tested. If a
  job cannot be finished, let player 1 do it alone and tell me which one it was.
"""),
])
print("package tooling and read-me are build 6 / disc v3")
