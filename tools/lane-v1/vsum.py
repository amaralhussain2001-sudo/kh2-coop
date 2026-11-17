"""Lane V1: condense a vprobe.txt: print a line only when layout shown, ours, game two-view flag, camera hold, room,
fade flags, step flag, camera 1 type, the twin pointer, camera 2's type or a lock-on flag change.
  python -I tools/lane-v1/vsum.py <vprobe.txt>"""
import re
import sys

PAT = re.compile(
    r"\s*(\d+) \| lay (\d)/\d \| ours (\d) \| req \d \| dual (\d) \| view \d \| hold (\d+) \| room (\w+) \| "
    r"fade (\d+ \d+) sw\d t(\d) c(\d) \| step (\d) \| cam1 type (\d+) tgt (\w+) \| cam2 tgt (\w+) \| eng (\w+) \| "
    r"twin (\w+)(?: \| c2type (\d+) lock2 (\d+) lock1 (\d+))?")
last = None
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    m = PAT.match(line)
    if not m:
        if "cave" in line:
            print(line.rstrip())
        continue
    key = m.groups()[1:11] + (m.group(15), m.group(16), m.group(17), m.group(18))
    if key != last:
        last = key
        print("%6s | shown %s | ours %s | dual %s | hold %s | room %s | fade %s task %s comp %s | step %s | cam1 type %s lock %s | twin %s | cam2 type %s lock %s" % (
            m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8), m.group(9),
            m.group(10), m.group(11), m.group(18), m.group(15), m.group(16), m.group(17)))
