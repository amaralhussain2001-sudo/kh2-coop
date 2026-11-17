"""Read timelines of tools/own/cap_log_probe2.py (ninth round, job 3) and sum up, for each run:
  * each hero's HELD stretches (the held bit, object + 0x160 bit 0x4000): how many, the longest, the longest stretch
    in ONE action, and the same for the stretches in which he is held and has NO hooked script;
  * the sixty-fifth glue's PAIRS: when each was made and forgotten, who was named, and the captures inside it
    (a mirror's capture has its return address inside the glue, 0x000ECF40 .. 0x000ED800);
  * captures of one hero while the other hero was held (a "split").
  python -I tools/own/holdstat.py <probe.txt> [...] [--pairs] [--splits]"""
import re
import sys

ACT = re.compile(r"^act f(\d+) P1 a([0-9A-F]+) held (\d) hook (\d) \(([^)]*)\) \| P2 a([0-9A-F]+) held (\d) hook (\d) \(([^)]*)\)")
CAP = re.compile(r"^cap c\d+ f(\d+) victim (\S+) move ([0-9A-F]+) captor (\S+) sender (\S+) script (\S+) player (\S+) ra ([0-9A-F]+)")
PAIR = re.compile(r"^pair f(\d+) (\S+) (\S+) captor (\S+) named (\S+)")
show_pairs, show_splits = "--pairs" in sys.argv, "--splits" in sys.argv


def stretches(rows, who, want):
    """rows: (frame, a1, held1, hook1, a2, held2, hook2). want(action, held, hook) -> bool. -> list of (start, length, action changes)"""
    out, start, acts = [], None, set()
    for r in rows:
        a, h, k = (r[1], r[2], r[3]) if who == 1 else (r[4], r[5], r[6])
        if want(a, h, k):
            if start is None:
                start, acts = r[0], set()
            acts.add(a)
        elif start is not None:
            out.append((start, r[0] - start, len(acts)))
            start = None
    if start is not None:
        out.append((start, rows[-1][0] - start, -len(acts)))
    return out


def one_action(rows, who, want):
    best, start, cur = 0, None, None
    for r in rows:
        a, h, k = (r[1], r[2], r[3]) if who == 1 else (r[4], r[5], r[6])
        if want(a, h, k):
            if cur != a:
                if start is not None:
                    best = max(best, r[0] - start)
                start, cur = r[0], a
        else:
            if start is not None:
                best = max(best, r[0] - start)
            start, cur = None, None
    if start is not None:
        best = max(best, rows[-1][0] - start)
    return best


for path in [a for a in sys.argv[1:] if not a.startswith("--")]:
    rows, caps, pairs = [], [], []
    for l in open(path, encoding="utf-8", errors="replace"):
        m = ACT.match(l)
        if m:
            if m.group(5) != m.group(9):
                rows.append((int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)), m.group(6), int(m.group(7)), int(m.group(8))))
            continue
        m = CAP.match(l)
        if m:
            caps.append((int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5), m.group(7), int(m.group(8), 16)))
            continue
        m = PAIR.match(l)
        if m:
            pairs.append((int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)))
    name = path.replace("\\", "/").split("/")[-1].replace("-probe.txt", "")
    if not rows:
        print("%s: no timeline lines" % name)
        continue
    s = "%-28s frames %d..%d" % (name, rows[0][0], rows[-1][0])
    for who in (1, 2):
        held = stretches(rows, who, lambda a, h, k: h == 1)
        bare = stretches(rows, who, lambda a, h, k: h == 1 and k == 0)
        s += " | P%d held %d times (longest %d, one action %d); held without a hook %d times (longest %d, one action %d)%s" % (
            who, len(held), max([x[1] for x in held], default=0), one_action(rows, who, lambda a, h, k: h == 1),
            len(bare), max([x[1] for x in bare], default=0), one_action(rows, who, lambda a, h, k: h == 1 and k == 0),
            "; HELD AT THE END since %d" % held[-1][0] if held and held[-1][2] < 0 else "")
    made = [p for p in pairs if p[1] != "-"]
    mirror = [c for c in caps if 0x000ECF40 <= c[6] < 0x000ED800]
    s += " | pairs %d, captures %d (mirrors %d)" % (len(made), len(caps), len(mirror))
    print(s)
    if show_pairs:
        for i, p in enumerate(pairs):
            if p[1] == "-":
                continue
            end = next((q[0] for q in pairs[i + 1:] if q[1] == "-"), rows[-1][0])
            inside = [c for c in caps if p[0] - 2 <= c[0] <= end]
            print("    pair f%d .. f%d (%d frames): %s + %s, captor %s, named %s; captures inside: %s" % (
                p[0], end, end - p[0], p[1], p[2], p[3], p[4],
                ", ".join("f%d %s %s%s" % (c[0], c[1], c[2], " (mirror)" if 0x000ECF40 <= c[6] < 0x000ED800 else "") for c in inside) or "none"))
    if show_splits:
        for c in caps:
            if 0x000ECF40 <= c[6] < 0x000ED800 or c[1] not in ("P1", "P2"):
                continue
            row = None
            for r in rows:
                if r[0] > c[0]:
                    break
                row = r
            if row is None:
                continue
            other_held = row[5] if c[1] == "P1" else row[2]
            if other_held:
                print("    split: f%d %s is captured (move %s, sender %s, the engine's player %s) while the other hero is held" % (
                    c[0], c[1], c[2], c[4], c[5]))
