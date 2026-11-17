"""One-off: the --nearest experiment of tools/merge/merge_v6.py becomes the twelfth glue of the build
(option --no-nearest takes it out)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "--no-nearest" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep("TWELFTH GLUE, AN EXPERIMENT (option --nearest; not with --helper, it uses the same hook): FOR AN OBJECT'S OWN\nTHINKING \"THE PLAYER\" IS THE HERO NEARER TO IT.",
    "TWELFTH GLUE (not together with the --helper experiment, it uses the same hook): FOR AN OBJECT'S OWN THINKING\n\"THE PLAYER\" IS THE HERO NEARER TO IT.")
rep("it offers and the moves it starts mean the nearer hero. Not sticky: the choice is made again at every step.",
    "it offers and the moves it starts mean the nearer hero. Not sticky: the choice is made again at every step.\nVERIFIED: the bag ride by player 2 alone (q3-bag-near, r1-bag-p2: gauge 100 -> 0, his own \"Jump\" prompt) and by\nplayer 1 alone (r1-bag-p1); Twilight Thorn 12,000 frames with both or only player 2 pressing, the \"Reversal\"\nprompt on player 2's screen, no crash (q4-thorn-near, r1-thorn-p2); the other special scenes unchanged (r1-*,\nr2-grand-near); all suites in sync; a hero alone unchanged.")
rep("[--no-board] [--helper] [--react] [--nearest]", "[--no-board] [--no-nearest] [--helper] [--react]")
rep('    if "--nearest" in sys.argv:        # EXPERIMENT\n        assert "--helper" not in sys.argv, "--nearest and --helper use the same hook"',
    '    if "--no-nearest" not in sys.argv and "--helper" not in sys.argv:')
p.write_text(t, encoding="utf-8")
print("ok")
