"""One-off: docs/STATE.md, the third helper try (option --helper2) and the soak tests of build 7."""
import pathlib
import sys

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "s1-mu-helper2" in t:
    raise SystemExit("already there")
soak = sys.argv[1] if len(sys.argv) > 1 else "(soak tests: see local\\t1.log, local\\t2.log)"
old = "   empty; the fresh save's party is the hero alone there), so it was deleted."
assert t.count(old) == 1
t = t.replace(old, old + r""" A third try (builder option
   `--helper2`: the helper in party place 2 thinks with the twin as the engine's player AND as party place 0):
   no change either, his positions are the same as without it to the unit (test s1-mu-helper2). So in that
   fight the helpers do not follow anybody; they go for the enemies.""")
old = "- Test discs added: `local\\iso\\test-s1-tt125.iso` (bag)"
assert t.count(old) == 1
t = t.replace(old, "- Soak on the final build 7: " + soak + "\n" + old)
p.write_text(t, encoding="utf-8")
print("state updated")
