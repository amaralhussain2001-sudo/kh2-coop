"""One-off: the test package's read-me goes to BUILD 10. The disc file is the SAME as in builds 8 and 9 (TEST v4);
only the game patch files changed (nineteenth glue: Summons with two heroes)."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path.name, t.count(old), old[:60])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


readme = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
if "TEST BUILD 10" in readme.read_text(encoding="utf-8"):
    raise SystemExit("already build 10")

edit(readme, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 9 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 10 (OWN SCREENS)"),
    ("""controller; Wisdom and Final Form were tried with player 2.
!! THE DISC FILE IS "TEST v4", THE SAME AS IN BUILD 8.""", """controller; Wisdom and Final Form were tried with player 2.
NEW IN BUILD 10: Summons work with two heroes, for either player (in build 9 the other hero sent every Summon
away at once); the dark form was tried with player 2.
TWO PCs IN THE SAME HOUSE: read "START-HERE (TWO PCs AT HOME).txt" first. It is shorter.
!! THE DISC FILE IS "TEST v4", THE SAME AS IN BUILDS 8 AND 9."""),
    ("""- NEW IN BUILD 9: the button-mash parts of some boss moves now listen to both controllers. Not seen in a test.
""", """- NEW IN BUILD 9: the button-mash parts of some boss moves now listen to both controllers. Not seen in a test.
- NEW IN BUILD 10: Summons (menu, second page, "Summon"). Either player can call one. The summoned friend comes
  to the hero who called him and fights beside that hero. His picture, the SUMMON gauge, "Dismiss" and his own
  commands show on the caller's screen only. Donald and Goofy leave while he is there and come back when he goes
  (Dismiss, or the gauge runs out). While one Summon is out the other player cannot call another one (his list
  is grey). When player 1 calls, the game shows its entrance movie on player 1's screen and both players wait
  for it. When player 2 calls there is no movie: the friend just appears. Tried with Genie and Peter Pan.
- NEW IN BUILD 10: the dark form (it can come by itself when a player starts a Drive Form) was tried with
  player 2: his hero turns dark, both helpers leave, his FORM gauge counts down, then everything is back.
- Known small thing: when a player walks into a new room while he is in a Drive Form, the emulator's log gets
  three fault lines. The form goes on normally.
"""),
    ("""- The dark form that comes by itself was not tried with two heroes (the five others were). If a form goes wrong,
  tell me which form and which player.
- NOT tested yet with two heroes: Summons, the guests' Limits, most bosses, most minigames, the Gummi Ship.
""", """- If a form goes wrong, tell me which form and which player.
- NOT tested yet with two heroes: the other Summons (Chicken Little, Stitch), walking into a new room while a
  Summon is out, the guests' Limits, most bosses, most minigames, the Gummi Ship.
"""),
])
