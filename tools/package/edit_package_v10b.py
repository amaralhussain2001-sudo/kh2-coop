"""One-off: the BUILD 10 read-me and the two-PC start text get the warning about Continue after a Game Over inside
a boss fight or a small game (never run on a real path; fifth round, part 8)."""
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
if "Continue after a Game Over INSIDE" in readme.read_text(encoding="utf-8"):
    raise SystemExit("already done")
edit(readme, [
    ("""- If a form goes wrong, tell me which form and which player.
""", """- If a form goes wrong, tell me which form and which player.
- NOT tested: Continue after a Game Over INSIDE a boss fight or a small game. (Continue after a Game Over in a
  normal room was tested and works.) SAVE OFTEN. If the game stops after "Continue" in such a fight: close it on
  both PCs, start again, choose Load Game, and tell me in which fight it was.
"""),
])
edit(HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt", [
    (""""OUT OF SYNC" on the screen almost always means two different picture qualities or two different folders.
""", """"OUT OF SYNC" on the screen almost always means two different picture qualities or two different folders.
SAVE OFTEN. One thing could not be tested: "Continue" after a Game Over inside a boss fight. If the game stops
there, close it on both PCs, start again and choose Load Game.
"""),
])
