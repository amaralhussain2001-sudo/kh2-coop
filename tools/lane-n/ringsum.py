"""Lane N: print the test-only trace of heals delivered by the script command (patch built with --debug, probe run
with --extra 000F2F80,000F2F84,000F2F88,000F2F8C,000F2F90,000F2F94,000F2F98).
  python -I tools/lane-n/ringsum.py <probe.txt>
Each line: frame, HP of every unit, heal counter, the last three (target <- caster) pairs with role names.
"""
import re
import sys

last = None
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.search(r"^\s*(\d+) .*000F2F80=(\w+) 000F2F84=(\w+) 000F2F88=(\w+) 000F2F8C=(\w+) 000F2F90=(\w+) 000F2F94=(\w+) 000F2F98=(\w+)", line)
    if not m:
        continue
    units = re.findall(r"(hero|twin|sid\d+)\[\w+\*?\] (-?\d+)/(\d+) mp (-?\d+) obj (\w+) fl (\w+)", line)
    names = {"%08X" % int(u[4], 16): u[0] for u in units}
    if m.group(2) != last:
        last = m.group(2)
        g = m.groups()
        pairs = ["%s <- %s" % (names.get(g[i], g[i]), names.get(g[i + 1], g[i + 1])) for i in (2, 4, 6)]
        pos = re.findall(r"(hero|twin|sid\d+)\[[^@]*@(-?\d+),(-?\d+),(-?\d+)", line)
        print("frame", g[0], " ".join("%s %s/%s%s" % (u[0], u[1], u[2], " DOWN" if int(u[5], 16) & 4 else "") for u in units),
              "| heals", int(g[1], 16), "| newest first:", "; ".join(pairs), "| pos", " ".join("%s(%s,%s)" % (q[0], q[1], q[3]) for q in pos))
