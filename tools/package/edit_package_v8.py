"""One-off: the test package goes to BUILD 8 with a NEW DISC FILE (TEST v4 = v3 + a second skateboard beside
every skateboard of the game and the five skate challenges for two): package builder, rehearsal copies, the
disc-maker script and the read-me files."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
V3_SHA = "23504a4bacc419144d68578192b8848519eda3ec"
V4_SHA = "97e37dd96ac1985946e80da502ba24d49a5ca3c7"


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path.name, t.count(old), old[:60])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


if "TEST v4" in (HERE / "make_test_package.py").read_text(encoding="utf-8"):
    raise SystemExit("already v4")

edit(HERE / "make_test_package.py", [
    ("(kh2-coop-v3.iso = v2 + Mail Delivery for two, since TEST build 6).",
     "(kh2-coop-v4.iso = v3 + a second skateboard everywhere, since TEST build 8)."),
    ('DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v3.kh2patch"', 'DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v4.kh2patch"'),
    ('DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"', 'DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v4).iso"'),
])
edit(HERE / "make_rehearsal_copies.py", [
    ("(local/iso/kh2-coop-v3.iso)", "(local/iso/kh2-coop-v4.iso)"),
    ('DISC = ROOT / "local" / "iso" / "kh2-coop-v3.iso"', 'DISC = ROOT / "local" / "iso" / "kh2-coop-v4.iso"'),
    ('DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"', 'DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v4).iso"'),
])
edit(HERE / "kit" / "MAKE-KH2-DISC" / "Make-KH2-Disc.ps1", [
    ('$PatchFile = Join-Path $Here "kh2-coop-v3.kh2patch"', '$PatchFile = Join-Path $Here "kh2-coop-v4.kh2patch"'),
    ('$OutName = "Kingdom Hearts II - Final Mix (2 Players TEST v3).iso"', '$OutName = "Kingdom Hearts II - Final Mix (2 Players TEST v4).iso"'),
    ('Fail "The file kh2-coop-v3.kh2patch is missing', 'Fail "The file kh2-coop-v4.kh2patch is missing'),
])
edit(HERE / "kit" / "HOW-TO-SET-UP (FRIEND).txt", [
    ('"TEST v2" file of the older builds is not used any more, delete it)',
     '"TEST v2" / "TEST v3" files of the older builds are not used any more, delete them)'),
])
edit(HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt", [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 7 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 8 (OWN SCREENS)"),
    ("""!! THE DISC FILE CHANGED IN BUILD 6. If you have an older build: replace the whole test folder with this one
   (both players) AND make the new disc file "TEST v3" (STEP 1). Delete the old "TEST v2" file.
""", """NEW IN BUILD 8: Donald and Goofy split up with you (when the two heroes are far apart, one helper goes with
each); every skateboard in the game has a second board beside it and the five skateboard challenges put both
players on a board; during a boss's scripted move the other player keeps his own picture; Valor and Master
Form were tried with player 2.
!! THE DISC FILE CHANGED AGAIN IN BUILD 8. Replace the whole test folder with this one (both players) AND make
   the new disc file "TEST v4" (STEP 1). Delete the old "TEST v2" / "TEST v3" files.
"""),
    ("""If you made the "TEST v1" or "TEST v2" disc file before: they are not used any more. Delete them from this
folder's MY-GAMES and make the v3 file (STEP 1). Only ONE Kingdom Hearts file may sit there.
""", """If you made a "TEST v1", "TEST v2" or "TEST v3" disc file before: they are not used any more. Delete them
from this folder's MY-GAMES and make the v4 file (STEP 1). Only ONE Kingdom Hearts file may sit there.
"""),
    ('"MY-GAMES (never share)":  Kingdom Hearts II - Final Mix (2 Players TEST v3).iso',
     '"MY-GAMES (never share)":  Kingdom Hearts II - Final Mix (2 Players TEST v4).iso'),
    ("       " + V3_SHA, "       " + V4_SHA),
    ('2. Game: the "2 Players TEST v3" file (new in build 6). Controllers: "2 players, no',
     '2. Game: the "2 Players TEST v4" file (new in build 8). Controllers: "2 players, no'),
    ("""  a door. ONE form at a time: while one hero is in a form the other's Drive row is dim (the game's own rule; a
  form uses up Donald or Goofy). Tested with Limit Form only.
""", """  a door. ONE form at a time: while one hero is in a form the other's Drive row is dim (the game's own rule; a
  form uses up Donald or Goofy). Tested for player 2 with Limit, Valor and Master Form (the helpers leave and
  come back as in the original game).
"""),
    ("""- NEW IN BUILD 6: skateboards. In the job Mail Delivery each player starts on his own board and has the board
  commands (Heelflip, Jump) in his own menu. In town each player can hop on a board of his own with Triangle.
""", """- NEW IN BUILD 6: skateboards. In the job Mail Delivery each player starts on his own board and has the board
  commands (Heelflip, Jump) in his own menu. A letter handed in by player 2 counts.
- NEW IN BUILD 8: a second skateboard stands beside every skateboard of the game (all worlds), so both players
  can ride in free roam. The five skateboard challenges (Twilight Town, Hollow Bastion, Agrabah, Halloween
  Town, Port Royal) put each player on a board; either player's tricks and checkpoints count, and either
  player can answer "Retry / Quit" at the end.
- NEW IN BUILD 8: Donald and Goofy (and a world's guest) belong to the team. While the two heroes are close
  together they follow player 1's hero as before. When the heroes are far apart (about 9 hero lengths), one
  helper goes with each hero, the one who is nearer to him. When the heroes meet again the helpers are one
  group again.
- NEW IN BUILD 8: a boss's scripted move (it grabs a hero, the camera shows the move). The player whose hero is
  in the move sees the move; the OTHER player keeps his own camera and can go on playing. The move's follow-up
  command (green, Triangle) belongs to the player whose hero is in the move.
"""),
    ("""- Donald and Goofy follow and help player 1's hero only.
""", """- Donald and Goofy stay with player 1's hero while the heroes are together (see above for far apart). Whom they
  heal first was not examined.
"""),
    ("""- Some full screens (the result screens of the small games, the shop) may still need player 1's buttons. Not
  tested with player 2's controller. The Game Over menu works with either controller.
- A boss move that grabs or carries a hero takes ONE hero (the nearer one). The other keeps playing. During such
  a move both screens can show the same picture for a moment.
""", """- Some full screens (the shop, the journal) may still need player 1's buttons. Not tested with player 2's
  controller. The Game Over menu and the "Retry / Quit" menu of the skateboard challenges work with either.
- A boss move that grabs or carries a hero takes ONE hero. Its opening moves always took player 1's hero in the
  first big boss fight of the Roxas part; later moves take whoever the boss reaches.
"""),
    ("""  player. In Mail Delivery both ride; handing in letters by player 2 and the end of the job were not tested. If a
  job cannot be finished, let player 1 do it alone and tell me which one it was.
""", """  player. In Mail Delivery both ride and both can hand in letters. If a job cannot be finished, let player 1 do
  it alone and tell me which one it was.
"""),
    ("""- Drive Forms other than Limit Form (Valor, Wisdom, Master, Final, and the dark one that comes by itself) are
  not tested with two heroes. If one goes wrong, tell me which form and which player.
""", """- Wisdom Form, Final Form and the dark form that comes by itself were not tried with two heroes (Valor, Master
  and Limit were). If one goes wrong, tell me which form and which player.
"""),
])
print("package tooling and read-me are build 8 / disc v4")
