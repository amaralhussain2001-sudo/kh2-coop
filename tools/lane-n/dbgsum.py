"""Lane N: print the test-only "who healed a player object" trace of a probe file (patch built with --debug and the
probe run with --extra 000F2FE0,000F2FE4,000F2FE8,000F2FEC).  python -I tools/lane-n/dbgsum.py <probe.txt>
Fields: return address of the caller of the take-a-hit method, attacker object, amount, target object.
"""
import re
import sys

last = None
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.search(r"^\s*(\d+) .*000F2FE0=(\w+) 000F2FE4=(\w+) 000F2FE8=(\w+) 000F2FEC=(\w+)", line)
    if not m:
        continue
    hp = re.findall(r"(hero|twin|sid\d+)\[\w+\*?\] (-?\d+)/\d+ mp (-?\d+) obj (\w+)", line)
    if m.groups()[1:] != last:
        last = m.groups()[1:]
        print("frame", m.group(1), " ".join("%s hp %s mp %s obj %s" % x for x in hp), "| hit delivered from", m.group(2),
              "attacker", m.group(3), "amount", int(m.group(4), 16), "target", m.group(5))
