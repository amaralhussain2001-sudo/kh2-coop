"""One-off: two sentences of the BUILD 9 read-me (the Trinity Limit was tried with player 2 after the first text
was written; test h2-flimit3-p2)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8")
pairs = [
    ("""  with Whirli-Goof and Comet. As in the original game the other helper leaves while a Limit runs.
""", """  with Whirli-Goof, Comet and Trinity. As in the original game the other helper leaves while a Limit runs.
"""),
    ("""- NOT tested yet with two heroes: Summons, the other Limits (Trinity and the guests' Limits), most bosses, most
  minigames, the Gummi Ship.
""", """- NOT tested yet with two heroes: Summons, the guests' Limits, most bosses, most minigames, the Gummi Ship.
"""),
]
for old, new in pairs:
    assert t.count(old) == 1, (t.count(old), old[:50])
    t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("read-me: Trinity sentences corrected")
