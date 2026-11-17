"""One-off: docs/STATE.md, the mission-gauge prizes were seen working (tests l5-mu-gp / l6-mu-nogp)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "l5-mu-gp" in t:
    raise SystemExit("already there")
old = "### 2. Prizes that fill a mission gauge: either hero (eighth glue; NOT tested in a game)"
assert t.count(old) == 1
t = t.replace(old, "### 2. Prizes that fill a mission gauge: either hero (eighth glue; VERIFIED later the same day)")
a = t.index("- HYPOTHESIS: these are the morale orbs of the Land of Dragons missions")
b = t.index("### 3. Rules screens and the Game Over menu on controller 2")
t = t[:a] + r"""- VERIFIED on the first morale mission (disc `local\iso\test-s1-mu68.iso`, player 1 idle, player 2 locks on
  with R1 and attacks; the same buttons on both builds): with the glue (l5-mu-gp) the morale gauge reads 79.7,
  80.7, 75.6, 58.9, 44.4, 34.4, 22.0, 7.0 at frames 5000-8900; without it (l6-mu-nogp, `--no-gprize`) 77.5,
  75.5, 70.2, 51.5, 36.9, 26.9, 14.5, 0.0 (mission lost). The gauge rises between 5000 and 5500 while only the
  twin is near the orbs (860 units from player 1's hero). So these prizes are the morale orbs.

""" + t[b:]
a = t.index("4. Not seen in a game yet: mission-gauge prizes for the second hero")
b = t.index('the six other "hits counted" missions;', a)
t = t[:a] + "4. Not seen in a game yet: " + t[b:]
p.write_text(t, encoding="utf-8")
print("state updated")
