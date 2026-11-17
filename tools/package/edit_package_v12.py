"""One-off: the test package goes to BUILD 12 with a NEW DISC FILE (TEST v5 = v4 + a second Light Cycle, a second
flying Sora in the Pooh game and a second carpet rider: tools/merge/build_disc_v5.py): package builder, rehearsal
copies, the two-PC step, the disc-maker script and the read-me files.
  python -I tools/package/edit_package_v12.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
V4_SHA = "97e37dd96ac1985946e80da502ba24d49a5ca3c7"
V5_SHA = "c0d652c46c603c093653d58f2506503a5089ce9c"
V4_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v4).iso"
V5_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso"


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) == 1:      # this pair is already in (the first run stopped half way)
            continue
        assert t.count(old) == 1, (path.name, t.count(old), old[:70])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


if "TEST v5" in (HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt").read_text(encoding="utf-8"):
    raise SystemExit("already v5")       # (the read-me is the LAST file edited: the guard holds only after a full run)

edit(HERE / "make_test_package.py", [
    ("(kh2-coop-v4.iso = v3 + a second skateboard everywhere, since TEST build 8).",
     "(kh2-coop-v5.iso = v4 + a second Light Cycle, Pooh flyer and carpet rider, since TEST build 12)."),
    ('DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v4.kh2patch"', 'DISC_PATCH = ROOT / "local" / "package" / "kh2-coop-v5.kh2patch"'),
    ('DISC_NAME = "%s"' % V4_NAME, 'DISC_NAME = "%s"' % V5_NAME),
])
edit(HERE / "make_rehearsal_copies.py", [
    ("(local/iso/kh2-coop-v4.iso)", "(local/iso/kh2-coop-v5.iso)"),
    ('DISC = ROOT / "local" / "iso" / "kh2-coop-v4.iso"', 'DISC = ROOT / "local" / "iso" / "kh2-coop-v5.iso"'),
    ('DISC_NAME = "%s"' % V4_NAME, 'DISC_NAME = "%s"' % V5_NAME),
])
edit(HERE / "finish_two_pcs.py", [
    ("(local/iso/kh2-coop-v4.iso, check number below)", "(local/iso/kh2-coop-v5.iso, check number below)"),
    ('SRC = ROOT / "local" / "iso" / "kh2-coop-v4.iso"', 'SRC = ROOT / "local" / "iso" / "kh2-coop-v5.iso"'),
    ('DST = OUT / "MY-GAMES (never share)" / "%s"' % V4_NAME,
     'DST = OUT / "MY-GAMES (never share)" / "%s"\n'
     'OLD = [OUT / "MY-GAMES (never share)" / ("Kingdom Hearts II - Final Mix (2 Players TEST v%%d).iso" %% n) for n in (1, 2, 3, 4)]' % V5_NAME),
    ('CHECK = "%s"' % V4_SHA, 'CHECK = "%s"' % V5_SHA),
    ('assert OUT.is_dir(), "run make_test_package.py first"\n',
     'assert OUT.is_dir(), "run make_test_package.py first"\n'
     'for old in OLD:                     # only ONE Kingdom Hearts file may sit in MY-GAMES (the dist folder is ours)\n'
     '    if old.exists():\n'
     '        old.unlink()\n'
     '        print("removed the older two-player disc file:", old.name)\n'),
])
edit(HERE / "kit" / "MAKE-KH2-DISC" / "Make-KH2-Disc.ps1", [
    ('$PatchFile = Join-Path $Here "kh2-coop-v4.kh2patch"', '$PatchFile = Join-Path $Here "kh2-coop-v5.kh2patch"'),
    ('$OutName = "%s"' % V4_NAME, '$OutName = "%s"' % V5_NAME),
    ('Fail "The file kh2-coop-v4.kh2patch is missing', 'Fail "The file kh2-coop-v5.kh2patch is missing'),
])
edit(HERE / "kit" / "HOW-TO-SET-UP (FRIEND).txt", [
    ('"TEST v2" / "TEST v3" files of the older builds are not used any more, delete them)',
     '"TEST v2" / "TEST v3" / "TEST v4" files of the older builds are not used any more, delete them)'),
])
edit(HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt", [
    ('It already holds the emulator, your BIOS, the patches and the two-player disc file ("TEST v4").',
     'It already holds the emulator, your BIOS, the patches and the two-player disc file ("TEST v5", new in build 12).'),
    ('2. BOTH PCs: Game = the "2 Players TEST v4" file.', '2. BOTH PCs: Game = the "2 Players TEST v5" file.'),
    ("""   (Copy the folder again whenever I give you a new build. Your saves are in emulator\\memcards\\Mcd001.ps2;
   keep that file if you want to keep them.)
""", """   (Copy the folder again whenever I give you a new build. Your saves are in emulator\\memcards\\Mcd001.ps2;
   keep that file if you want to keep them.)
   BUILD 12 HAS A NEW DISC FILE ("TEST v5"). Delete the old folder on the second PC and copy this one.
"""),
    ("""SAVE OFTEN. "Continue" after a Game Over inside a boss fight was tested in one fight only (it goes back to the
room before the fight and plays its scene again; START skips it). If the game ever stops there, close it on both
PCs, start again and choose Load Game.
""", """SAVE OFTEN. "Continue" after a Game Over inside a fight was tested in three fights (it goes back to the room
before the fight and plays its scene again; START skips it). If the game ever stops there, close it on both PCs,
start again and choose Load Game.
"""),
])
edit(HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt", [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 11 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 12 (OWN SCREENS)"),
    ("""TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.
!! THE DISC FILE IS "TEST v4", THE SAME AS IN BUILDS 8 AND 9. If you never made it: make it now (STEP 1). If you have
   older files ("TEST v2" / "TEST v3"): delete them. Replace the whole test folder with this one (both players).
""", """NEW IN BUILD 12: the Gummi Ship for two (player 2 flies his own ship); the Light Cycle, the Pooh flying game and
the Magic Carpet for two; where a small game has only one hero (the carpet escape, the toy cannon, the sidecar)
both controllers drive him; the world map, the Moogle's workshop and the end menus of the small games work with
player 2's controller; Donald's and Goofy's items reach player 2; after a "Continue" player 2 has his own Drive
and Summon values again; three sources of fault lines of build 11 are closed. Every mission of the game was
started once with two heroes by a test script.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.
!! THE DISC FILE CHANGED IN BUILD 12: it is "TEST v5" now. Replace the whole test folder with this one (both
   players) and delete the older disc files ("TEST v2" / "TEST v3" / "TEST v4"). Two PCs at home: the folder
   already holds the new disc file. Friends: make it with STEP 1.
"""),
    ("""If you made a "TEST v1", "TEST v2" or "TEST v3" disc file before: they are not used any more. Delete them
from this folder's MY-GAMES and make the v4 file (STEP 1). Only ONE Kingdom Hearts file may sit there.
""", """If you made a "TEST v1" to "TEST v4" disc file before: they are not used any more. Delete them from this
folder's MY-GAMES and make the v5 file (STEP 1). Only ONE Kingdom Hearts file may sit there.
"""),
    ('"MY-GAMES (never share)":  %s' % V4_NAME, '"MY-GAMES (never share)":  %s' % V5_NAME),
    ("       " + V4_SHA, "       " + V5_SHA),
    ('2. Game: the "2 Players TEST v4" file (new in build 8). Controllers: "2 players, no',
     '2. Game: the "2 Players TEST v5" file (new in build 12). Controllers: "2 players, no'),
    ("""- NEW IN BUILD 10: the dark form (it can come by itself when a player starts a Drive Form) was tried with
""", """- NEW IN BUILD 12: THE GUMMI SHIP. Player 2 has his own ship: his stick flies it, his Circle fires its guns,
  his shots count for the one score. His START opens the pause menu. The Gummi Menu, the pause menu, the
  results and "Retry" listen to either controller. All nine routes were flown by a script with two ships.
  What his ship does not have yet: the enemies cannot damage it, and the flight is lost when PLAYER 1's ship
  is destroyed. There is one hull gauge (player 1's ship). Both ships look the same; player 2's starts a
  little to the right.
- NEW IN BUILD 12: THE SPECIAL RIDES. The new disc file gives player 2 his own Light Cycle (Space Paranoids),
  his own flying Sora in the Pooh game with the balloon, and his own rider in the Magic Carpet parts of
  Agrabah (the fights in the ruins, the race to the tower, Jafar). Each is moved by its own controller.
  Two things to know: on the carpet, player 2's hero flies in the riding pose WITHOUT a carpet under him (the
  one carpet stays under player 1's hero); it looks odd and works. On the Light Cycle the ride is over when
  EITHER cycle is destroyed, as the game does it for one rider; nobody can be picked up there.
- NEW IN BUILD 12: WHEN PLAYER 2 HAS NO HERO, HIS CONTROLLER DRIVES PLAYER 1'S. Three small games have room
  for one hero only: the carpet escape from the ruins, the toy cannon (Gift Wrapping) and the sidecar near
  the end. There both controllers steer and shoot the one hero or cannon, and both screens show the same
  picture. The title menu and other screens without a hero listen to either controller too.
- NEW IN BUILD 12: the world map (fly, "Land" with Triangle), the Moogle's workshop and the "Retry / Quit"
  menu at the end of a small game work with player 2's controller.
- NEW IN BUILD 12: when Donald or Goofy uses a Potion, it goes to the hero who has less HP (before, always to
  player 1's hero).
- NEW IN BUILD 12: after "Continue" player 2 has the Drive gauge, the form and the Summon he had when he came
  into the room, as player 1 always had. (In build 11 a Summon he had brought into the room left at once.)
- NEW IN BUILD 12: Limits were tested again. They work for player 2 also when the heroes are far apart. A
  Limit needs a fight; in a quiet room the list is grey for both players, as in the original game.
- NEW IN BUILD 12: three sources of fault lines are closed: the game ran out of green command signs in long
  boss fights (it has twice as many now), a Drive Form carried through a door, and magic effects that had
  ended. Also a grey square in place of player 2's menu during "READY GO!" and an orange glint beside his
  gauge in the first town.
- NEW IN BUILD 10: the dark form (it can come by itself when a player starts a Drive Form) was tried with
"""),
    ("""- Known small thing: when a player walks into a new room while he is in a Drive Form, the emulator's log gets
  three fault lines. The form goes on normally.
- Known small thing: Stitch walks on the screen glass. He shows on BOTH screens, whoever called him.
- Known small thing: while the two heroes are far apart (Donald with one, Goofy with the other), player 2's
  Limits are grey. Come together again to use them.
""", """- Known small thing: Stitch walks on the screen glass. He shows on BOTH screens, whoever called him.
- Known small thing: the sound is one sound for both PCs. You hear the game from player 1's camera.
"""),
    ("""- The item shop, the main menu with its pages, the save menu, the Game Over menu and the "Retry / Quit" menu
  of the skateboard challenges work with either controller. Other full screens (the Moogle's workshop, the
  world map, result screens of small games) were not tried with player 2's controller.
""", """- The item shop, the Moogle's workshop, the main menu with its pages, the save menu, the world map, the Gummi
  Menu, the Game Over menu and the "Retry / Quit" menus work with either controller.
- Some small games listen for a button on EITHER controller where the game means "the rider" (the whirlwinds
  in the Land of Dragons, for example): a press by one player can count for the other's ride.
"""),
    ("""- Continue after a Game Over inside a boss fight was tested in ONE fight (the first big boss) with a test line
  that gives the test disc the room memory a real game has. Still: SAVE OFTEN. If the game ever stops after
  "Continue": close it on both PCs, start again, choose Load Game, and tell me in which fight it was.
- NOT tested yet with two heroes: saving while a Summon is out, the guests' Limits, most bosses, most
  minigames, the Gummi Ship, the Moogle's workshop and the world map with player 2's controller.
""", """- Continue after a Game Over inside a fight was tested in three fights (two bosses and a small game) with a
  test line that gives the test disc the room memory a real game has. Still: SAVE OFTEN. If the game ever
  stops after "Continue": close it on both PCs, start again, choose Load Game, and tell me in which fight.
- Every mission of the game (302 of them) was STARTED once with two heroes by a test script: the first two
  and a half minutes of each, with level 1 heroes. No script played a boss or a small game to its end, and no
  script can judge how a fight feels. That is your part.
- Saving while a Summon is out works: after loading, the Summon is there again and belongs to the player who
  called it. Player 2's gauge after a load is not the one from the moment of saving (a saved game holds
  player 1's values only).
"""),
])
print("package tooling and read-me are build 12 / disc v5")
