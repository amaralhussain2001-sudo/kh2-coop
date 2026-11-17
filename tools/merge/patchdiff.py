"""Compare patch files word by word.

  python -I tools/merge/patchdiff.py delta <base> <lane> [<against>]
      prints what <lane> adds to, changes in or removes from <base> (folders under patches/ or .pnach paths);
      with <against>: also lists every address of that delta that <against> already writes (a clash to resolve).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
NAME = "SLPM-66675_F266B00B.pnach"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})")


def load(x):
    p = pathlib.Path(x)
    if not p.is_file():
        p = ROOT / "patches" / x / NAME
    d = {}
    for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw.strip())
        if m:
            d[(m.group(1), m.group(3).lower(), int(m.group(2), 16))] = int(m.group(4), 16)
    return d


def ranges(addrs):
    out, start, prev = [], None, None
    for a in sorted(addrs):
        if start is None:
            start = prev = a
        elif a == prev + 4:
            prev = a
        else:
            out.append((start, prev))
            start = prev = a
    if start is not None:
        out.append((start, prev))
    return out


def delta(base, lane):
    added = {k: v for k, v in lane.items() if k not in base}
    changed = {k: v for k, v in lane.items() if k in base and base[k] != v}
    removed = [k for k in base if k not in lane]
    return added, changed, removed


def main():
    if len(sys.argv) < 4 or sys.argv[1] != "delta":
        sys.exit(__doc__)
    base, lane = load(sys.argv[2]), load(sys.argv[3])
    added, changed, removed = delta(base, lane)
    print("base %d words, lane %d words: added %d, changed %d, removed %d" % (len(base), len(lane), len(added), len(changed), len(removed)))
    for s, e in ranges(k[2] for k in added):
        print("  added   %08X-%08X (%d words)" % (s, e + 3, (e - s) // 4 + 1))
    for k in sorted(changed, key=lambda x: x[2]):
        print("  changed %08X: %08X -> %08X" % (k[2], base[k], changed[k]))
    for s, e in ranges(k[2] for k in removed):
        print("  removed %08X-%08X (%d words)" % (s, e + 3, (e - s) // 4 + 1))
    if len(sys.argv) > 4:
        against = load(sys.argv[4])
        hits = sorted(k[2] for k in list(added) + list(changed) + removed if k in against and (k not in base or against[k] != base[k]))
        print("addresses of this delta that %s writes differently from the base: %d" % (sys.argv[4], len(hits)))
        for a in hits:
            print("  CLASH %08X" % a)


if __name__ == "__main__":
    main()
