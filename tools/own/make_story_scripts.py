"""TEST ONLY (ninth round, job 5): player 1's script for a small game entered from the story: New Game, then ONLY
Triangle every 30 frames (to take the talk point's command) up to <switch>, then the lines of another script.
  python -I tools/own/make_story_scripts.py <out.txt> <switchFrame> <scriptForAfter.txt>"""
import pathlib
import sys

out, switch, after = pathlib.Path(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
lines = ["# TEST (ninth round, a small game entered from the story): New Game, Triangle every 30 frames from 4700 to %d, then %s." % (switch, after.name)]
lines += ["%d 4 O" % f for f in range(3000, 3601, 120)]
lines += ["%d 4 TRI" % f for f in range(4700, switch, 30)]
for l in after.read_text(encoding="utf-8").splitlines():
    p = l.split()
    if p and p[0].isdigit() and int(p[0]) >= switch:
        lines.append(l)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(lines), "lines")
