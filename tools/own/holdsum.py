"""Read a hold timeline (tools/own/act_poll_probe.py: a line whenever a hero's action word changes) and sum up
each hero's CAPTURED MOTIONS (action FC .. FF = held in a boss's paired move): how many holds, how long each
lasted, whether one is still on at the end of the run, and how often BOTH heroes were held at the same time.
  python -I tools/own/holdsum.py <probe.txt> [<probe.txt> ...]
A "hold" = a stretch of frames in which the hero's action stays inside FC .. FF (changes between FC, FD, FE, FF
do not end it). Lines on which both heroes stand at exactly the same place are left out: the probe then caught
the moment in which the engine's player pointer holds the twin."""
import re
import sys

LINE = re.compile(r"^(?:act )?f(\d+) P1 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\)).*?\| P2 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\))")


def held(a):
    return a in ("FC", "FD", "FE", "FF")


for path in sys.argv[1:]:
    rows = []
    for l in open(path, encoding="utf-8", errors="replace"):
        m = LINE.match(l)
        if m and m.group(3) != m.group(5):        # (the same place for both = the probe caught the moment in which the
            rows.append((int(m.group(1)), m.group(2), m.group(4)))      # engine's player pointer holds the twin: not a real line)
    if not rows:
        print("%s: no timeline lines" % path)
        continue
    last = rows[-1][0]
    out = []
    for who in (1, 2):
        holds, start = [], None
        for f, a1, a2 in rows:
            h = held(a1 if who == 1 else a2)
            if h and start is None:
                start = f
            elif not h and start is not None:
                holds.append((start, f - start, True))
                start = None
        if start is not None:
            holds.append((start, last - start, False))
        longest = max([h[1] for h in holds], default=0)
        open_end = [h for h in holds if not h[2]]
        out.append("P%d %d holds (longest %d frames%s)" % (who, len(holds), longest,
                   "; STILL HELD AT THE END since %d" % open_end[0][0] if open_end else ""))
    both, prev = 0, False
    for f, a1, a2 in rows:
        b = held(a1) and held(a2)
        if b and not prev:
            both += 1
        prev = b
    name = path.replace("\\", "/").split("/")[-1].replace("-probe.txt", "")
    print("%-34s frames %d..%d | %s | %s | both held at once: %d times" % (name, rows[0][0], last, out[0], out[1], both))
