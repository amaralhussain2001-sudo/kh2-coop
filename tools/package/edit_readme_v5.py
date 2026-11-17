"""One-off: turn the kit read-me of TEST build 4 into TEST build 5 (Drive Forms for player 2, hit counters, rules
screens on either controller, the empty command menu after a rules screen)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8")
if "TEST BUILD 5" in t:
    raise SystemExit("already build 5")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


rep("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 4 (OWN SCREENS)",
    "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 5 (OWN SCREENS)")
rep("""If you have build 3: replace the whole test folder with this one (both players). The disc file stays the same.
""", """NEW IN BUILD 5: player 2 can use Drive Forms (his own form, his own form gauge, his own menu); the two fights
where the enemy cannot be hurt now count player 2's hits; a small game's rules screen can be closed by either
player; the command menu no longer stays empty after a rules screen.
If you have build 3 or 4: replace the whole test folder with this one (both players). The disc file stays the same.
""")
rep("""- Saving works (one shared save). The save holds player 1's Drive gauge; after loading, both heroes start with it.
""", """- Saving works (one shared save). The save holds player 1's Drive gauge; after loading, both heroes start with it.
- NEW: Drive Forms for both players. Each player picks Drive in his own menu. Only that player's hero changes;
  he gets the form's gauge and the commands "Revert" and the form's own on his screen. He keeps the form through
  a door. ONE form at a time: while one hero is in a form the other's Drive row is dim (the game's own rule; a
  form uses up Donald or Goofy). Tested with Limit Form only.
- NEW: in the two fights where the enemy cannot be hurt (Roxas, with the Struggle bat) player 2's hits count, so
  the story goes on whoever fights. The same rule is in six later fights of this kind.
- NEW: the rules screen of a small game (Struggle, the jobs) can be closed by either player.
""")
rep("""- Some full screens (the rules and result screens of the small games, the shop) may still need player 1's
  buttons. Not tested with player 2's controller.
""", """- Some full screens (the result screens of the small games, the shop) may still need player 1's buttons. Not
  tested with player 2's controller. The Game Over menu works with either controller.
""")
rep("""- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard), the bag job, and the counter of two "hit them N times" fights does not
  count player 2's hits. If a job cannot be finished, let player 1 do it alone and tell me which one it was.
""", """- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard) and the bag job. If a job cannot be finished, let player 1 do it alone and
  tell me which one it was.
""")
rep("""- NOT tested yet with two heroes: Drive Forms, Limits, Summons, most bosses, most minigames, the Gummi Ship,
  shops and the journal with own screens.""", """- Drive Forms other than Limit Form (Valor, Wisdom, Master, Final, and the dark one that comes by itself) are
  not tested with two heroes. If one goes wrong, tell me which form and which player.
- NOT tested yet with two heroes: Limits, Summons, most bosses, most minigames, the Gummi Ship, shops and the
  journal with own screens.""")
p.write_text(t, encoding="utf-8")
print("read-me is build 5")
