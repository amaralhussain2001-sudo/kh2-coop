"""One-off: the read-me and the two-PC start text of the test package become BUILD 11 (sixth round):
Continue inside a boss fight was tested, a room change with a Summon out was fixed, Chicken Little and Stitch
were tried, the known small things of Summons and Limits."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path.name, t.count(old), old[:60])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8", newline="\n")
    print("edited", path.name)


readme = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
if "TEST BUILD 11" in readme.read_text(encoding="utf-8"):
    raise SystemExit("already done")
edit(readme, [
    ("TEST BUILD 10 (OWN SCREENS)", "TEST BUILD 11 (OWN SCREENS)"),
    ("""away at once); the dark form was tried with player 2.
""", """away at once); the dark form was tried with player 2.
NEW IN BUILD 11: a Summon stays right when you walk into a new room (in build 10 the OTHER player's Drive gauge
turned into an empty SUMMON gauge after a door); "Continue" after a Game Over inside a boss fight was tested and
works; Chicken Little and Stitch were tried; a hidden fault of builds 9 and 10 in long boss fights is closed.
"""),
    ("""  for it. When player 2 calls there is no movie: the friend just appears. Tried with Genie and Peter Pan.
""", """  for it. When player 2 calls there is no movie: the friend just appears. Tried with all four (Chicken Little,
  Genie, Stitch, Peter Pan).
- NEW IN BUILD 11: a Summon and a door. The friend comes along into the next room and his gauge goes on, on the
  caller's screen; the other player keeps his own Drive gauge. A Summon is not possible while the other player
  is in a Drive Form that uses up a helper (the names in the list are grey): this is the game's own rule.
- NEW IN BUILD 11: "Continue" after a Game Over inside a boss fight. The game goes back to the last normal room
  it remembered, plays that room's story scene again (press START to skip it) and starts the fight again, with
  both heroes and both views. Tested in the first big boss fight. This is how the original game does it.
- NEW IN BUILD 11: a Game Over while a Summon is out: Continue brings both heroes back. A Summon that player 2
  had already brought into the room leaves right after the Continue (he can call it again when his gauge is
  full); nothing else changes.
- NEW IN BUILD 11: a hidden fault of builds 9 and 10 is closed. In a long boss fight, after player 2 had used a
  boss move's follow-up command, the game could run out of its green command signs and then wrote to a wrong
  place in memory (50 fault lines in the log; in the test nothing bad followed, but it was luck). Now the game
  can no longer run out. Player 2's green sign may be missing for a moment in such a fight; the command
  itself is still in his menu.
"""),
    ("""- Known small thing: when a player walks into a new room while he is in a Drive Form, the emulator's log gets
  three fault lines. The form goes on normally.
""", """- Known small thing: when a player walks into a new room while he is in a Drive Form, the emulator's log gets
  three fault lines. The form goes on normally.
- Known small thing: Stitch walks on the screen glass. He shows on BOTH screens, whoever called him.
- Known small thing: while the two heroes are far apart (Donald with one, Goofy with the other), player 2's
  Limits are grey. Come together again to use them.
"""),
    ("""- NOT tested: Continue after a Game Over INSIDE a boss fight or a small game. (Continue after a Game Over in a
  normal room was tested and works.) SAVE OFTEN. If the game stops after "Continue" in such a fight: close it on
  both PCs, start again, choose Load Game, and tell me in which fight it was.
- NOT tested yet with two heroes: the other Summons (Chicken Little, Stitch), walking into a new room while a
  Summon is out, the guests' Limits, most bosses, most minigames, the Gummi Ship.
""", """- Continue after a Game Over inside a boss fight was tested in ONE fight (the first big boss) with a test line
  that gives the test disc the room memory a real game has. Still: SAVE OFTEN. If the game ever stops after
  "Continue": close it on both PCs, start again, choose Load Game, and tell me in which fight it was.
- NOT tested yet with two heroes: saving while a Summon is out, the guests' Limits, most bosses, most
  minigames, the Gummi Ship, the Moogle's workshop and the world map with player 2's controller.
"""),
])
edit(HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt", [
    ("""SAVE OFTEN. One thing could not be tested: "Continue" after a Game Over inside a boss fight. If the game stops
there, close it on both PCs, start again and choose Load Game.
""", """SAVE OFTEN. "Continue" after a Game Over inside a boss fight was tested in one fight only (it goes back to the
room before the fight and plays its scene again; START skips it). If the game ever stops there, close it on both
PCs, start again and choose Load Game.
"""),
])
