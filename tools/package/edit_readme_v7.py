"""One-off: turn the kit read-me of TEST build 6 into TEST build 7 (the nearer hero is "the player" for things in
the room: the bag job, boss prompts)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8")
if "TEST BUILD 7" in t:
    raise SystemExit("already build 7")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


rep("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 6 (OWN SCREENS)",
    "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 7 (OWN SCREENS)")
rep("""!! THE DISC FILE CHANGED IN BUILD 6.""", """NEW IN BUILD 7: things in the room now deal with the hero who is NEARER to them. So player 2 can ride the bag
of the Seven Wonders, and a boss's green command (Triangle) goes to the player who stands nearer.
!! THE DISC FILE CHANGED IN BUILD 6.""")
rep("""- NEW IN BUILD 6: skateboards.""", """- NEW IN BUILD 7: the nearer hero counts. A thing in the room (the moving bag, a boss, a chest) offers its green
  Reaction Command to the hero who is nearer to it, on that player's screen. A hero who is down is skipped.
  So either player can do the bag job, and either player can answer a boss's command.
- NEW IN BUILD 6: skateboards.""")
rep("""- Boss moves that grab or carry the hero take player 1's hero only (seen with the first big boss of the Roxas
  part). Player 2 keeps playing during them.
""", """- A boss move that grabs or carries a hero takes ONE hero (the nearer one). The other keeps playing. During such
  a move both screens can show the same picture for a moment.
""")
rep("""- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: the bag job.
  In Mail Delivery both ride now;""", """- The first hours (Roxas in Twilight Town) are full of special jobs. All of them can now be done by either
  player. In Mail Delivery both ride;""")
p.write_text(t, encoding="utf-8")
print("read-me is build 7")
