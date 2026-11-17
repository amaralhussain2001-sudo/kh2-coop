"""One-off: the test package's read-me goes to BUILD 9. The disc file is the SAME as in build 8 (TEST v4); only the
game patch files changed (fifteenth to seventeenth glue, own screens step 9)."""
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
if "TEST BUILD 9" in readme.read_text(encoding="utf-8"):
    raise SystemExit("already build 9")

edit(readme, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 8 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 9 (OWN SCREENS)"),
    ("""!! THE DISC FILE CHANGED AGAIN IN BUILD 8. Replace the whole test folder with this one (both players) AND make
   the new disc file "TEST v4" (STEP 1). Delete the old "TEST v2" / "TEST v3" files.
""", """NEW IN BUILD 9: a boss move's green follow-up command goes to the player whose hero is in the move; one player
on a skateboard and one on foot each see their own right menu; Donald and Goofy heal player 2's hero too; a
Limit (team attack) started by player 2 is his to play; the item shop and the journal work with player 2's
controller; Wisdom and Final Form were tried with player 2.
!! THE DISC FILE IS "TEST v4", THE SAME AS IN BUILD 8. If you never made it: make it now (STEP 1). If you have
   older files ("TEST v2" / "TEST v3"): delete them. Replace the whole test folder with this one (both players).
"""),
    ("""  form uses up Donald or Goofy). Tested for player 2 with Limit, Valor and Master Form (the helpers leave and
  come back as in the original game).
""", """  form uses up Donald or Goofy). Tested for player 2 with Limit, Valor, Wisdom, Master and Final Form (the
  helpers leave and come back as in the original game).
- NEW IN BUILD 9: a Game Over while player 2 is in a form: Continue brings both heroes back, and he is still
  in his form.
"""),
    ("""  commands (Heelflip, Jump) in his own menu. A letter handed in by player 2 counts.
""", """  commands (Heelflip, Jump) in his own menu. A letter handed in by player 2 counts. The whole job was played to
  its end with both players handing in letters: "CLEAR!", the pay, and both heroes back in the street.
"""),
    ("""  in the move sees the move; the OTHER player keeps his own camera and can go on playing. The move's follow-up
  command (green, Triangle) belongs to the player whose hero is in the move.
""", """  in the move sees the move; the OTHER player keeps his own camera and can go on playing.
- NEW IN BUILD 9: the move's follow-up command (green, Triangle; "Break Raid" in the first big boss fight) shows
  in the menu of the player whose hero is in the move, and that player's Triangle starts it. (In build 8 it sat
  in player 1's menu.)
- NEW IN BUILD 9: skateboards in town with ONE rider. The rider has the board menu, the walker has his normal
  menu (in build 8 the walker's menu looked broken). On a board: Square = get off.
- NEW IN BUILD 9: Donald and Goofy heal BOTH heroes, with Cure and with items. Their order: the helper himself,
  the hero he follows, the other hero, the other helper. (Before, player 2's hero was never healed while all
  were together.)
- NEW IN BUILD 9: the item shop and the pages of the main menu (Journal, Config) can be opened and used with
  player 2's controller. Both screens show the shop or the menu while it is open.
- NEW IN BUILD 9: Limits (menu, second page, "Limit"). Either player can start a Limit with Donald or Goofy.
  The Limit's own commands show in the menu of the player who started it, and he plays it to the end. (In build
  8 a Limit started by player 2 put its commands into player 1's menu and stopped after the first move.) Tried
  with Whirli-Goof and Comet. As in the original game the other helper leaves while a Limit runs.
- NEW IN BUILD 9: the button-mash parts of some boss moves now listen to both controllers. Not seen in a test.
"""),
    ("""- Donald and Goofy stay with player 1's hero while the heroes are together (see above for far apart). Whom they
  heal first was not examined.
""", """- Donald and Goofy stay with player 1's hero while the heroes are together (see above for far apart).
- When one player's menu changes its look (he hops on or off a skateboard), the rows of the other player's menu
  can blink for a moment.
"""),
    ("""- Some full screens (the shop, the journal) may still need player 1's buttons. Not tested with player 2's
  controller. The Game Over menu and the "Retry / Quit" menu of the skateboard challenges work with either.
""", """- The item shop, the main menu with its pages, the save menu, the Game Over menu and the "Retry / Quit" menu
  of the skateboard challenges work with either controller. Other full screens (the Moogle's workshop, the
  world map, result screens of small games) were not tried with player 2's controller.
"""),
    ("""- When a boss's move grabs PLAYER 2's hero and a green follow-up command appears, it shows in PLAYER 1's menu and
  only player 1's Triangle starts it (seen with "Break Raid" in the first big boss fight). Player 1: press
  Triangle for your friend when you see it. If nobody presses, the move simply ends with some damage.
- Skateboards in town: while only ONE player is on a board, the other player's command menu is drawn with the
  wrong frame (it looks broken but still works). It is right again when he hops on his own board (Triangle,
  "Hop On") or when the rider gets off. The skateboard jobs and challenges are not affected.
""", ""),
    ("""- Wisdom Form, Final Form and the dark form that comes by itself were not tried with two heroes (Valor, Master
  and Limit were). If one goes wrong, tell me which form and which player.
- NOT tested yet with two heroes: Limits, Summons, most bosses, most minigames, the Gummi Ship, shops and the
  journal with own screens.
""", """- The dark form that comes by itself was not tried with two heroes (the five others were). If a form goes wrong,
  tell me which form and which player.
- NOT tested yet with two heroes: Summons, the other Limits (Trinity and the guests' Limits), most bosses, most
  minigames, the Gummi Ship.
"""),
])
print("the read-me is build 9 (disc v4, unchanged)")
