"""Lane S1: compact summary of a test's probe.txt (one line per probed frame).

  python -I tools/lane-s1/s1sum.py <test-name> [<test-name> ...]
Per frame: room, battle flag, program numbers (map/btl/evt), the two heroes (controller, HP, position, action),
the other unit slots (HP/max; id -1 = enemy or object with HP), mission counters (first word of point1..3)
and the first gauge words, the mission timer word.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def summarize(test):
    f = ROOT / "local" / "tests" / test / "probe.txt"
    if not f.exists():
        return ["%s: no probe file" % test]
    out = ["== " + test]
    cur = None
    blocks = []
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"frame (\d+):(.*)", line)
        if m:
            cur = {"frame": int(m.group(1)), "head": m.group(2), "lines": []}
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for b in blocks:
        if "failed" in b["head"]:
            out.append("  f%d: probe failed" % b["frame"])
            continue
        room = re.search(r"room (\w+) battle (\d)", b["head"])
        heroes, slots, pts, gauges, now, timer = [], "", [], [], "", ""
        for l in b["lines"]:
            s = l.strip()
            m = re.match(r"hero (\w+) pos \(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\) (\w+)\s+slot (\d+) HP (\d+)/(\d+).*?\[(.*?)\] ctl (\w+) act (\w+)", s)
            if m:
                who = "twin" if "twin" in m.group(9) else "hero"
                heroes.append("%s(%s) HP %s/%s at (%.0f,%.0f,%.0f) act %s" % (who, m.group(5), m.group(7), m.group(8),
                              float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(11)))
            elif s.startswith("slots:"):
                others = re.findall(r"(\d+): id (-?\d+) HP (-?\d+)/(-?\d+)", s)
                slots = " ".join("%s/%s" % (hp, mx) for n, i, hp, mx in others if i == "-1")
            elif s.startswith("point"):
                w = s.split()
                pts.append(str(int(w[1], 16)))
            elif s.startswith("gauge"):
                w = s.split("|")[0].split()
                gauges.append(",".join(w[1:3]))
            elif s.startswith("now "):
                m2 = re.match(r"now (\w+) events (\w+) (\w+)", s)
                if m2:
                    now = "now %s ev %s %s" % (m2.group(1), m2.group(2), m2.group(3))
            elif s.startswith("timer block"):
                w = s.split("|")[0].split()
                timer = "timer %s/%s" % (w[8], w[7]) if len(w) > 8 else ""
        out.append("  f%d: room %s btl %s | %s | %s | others [%s] | points %s | gauges %s | %s" % (
            b["frame"], room.group(1) if room else "?", room.group(2) if room else "?", now, "; ".join(heroes) or "NO HERO OBJECTS",
            slots, "/".join(pts[:3]), " ".join(gauges[:2]), timer))
    return out


for t in sys.argv[1:]:
    print("\n".join(summarize(t)))
