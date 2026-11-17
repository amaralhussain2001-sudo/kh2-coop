"""Read a hold timeline (tools/own/act_poll_probe.py) and print it CLEANED for a range of frames: the lines on which
both heroes stand at exactly the same place are left out (the probe caught the moment in which the engine's
player pointer holds the twin), and a line is printed only when a hero's action differs from the line before.
  python -I tools/own/holdline.py <probe.txt> <fromFrame> <toFrame>"""
import re
import sys

LINE = re.compile(r"^(?:act )?f(\d+) P1 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\)).*?\| P2 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\))")
a, b = int(sys.argv[2]), int(sys.argv[3])
prev = None
for l in open(sys.argv[1], encoding="utf-8", errors="replace"):
    m = LINE.match(l)
    if not m or m.group(3) == m.group(5):
        continue
    f = int(m.group(1))
    cur = (m.group(2), m.group(4))
    if cur != prev and a <= f <= b:
        print("f%d P1 a%s %s | P2 a%s %s" % (f, m.group(2), m.group(3), m.group(4), m.group(5)))
    prev = cur
