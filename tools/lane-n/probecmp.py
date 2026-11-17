"""Lane N: compare two probe files frame by frame (frames sampled in both).  python -I tools/lane-n/probecmp.py A B
Compared per frame: room, fight state, Game Over flag and for every unit: slot, HP, max HP, MP, flags, motion, timer,
position. Lane N's own variables are not compared (they differ by design between patch variants).
"""
import re
import sys


def load(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*(\d+) room (\w+) btl (\d) go (\d) nvars [0-9A-F ]*\| (.*)", line)
        if m:
            rest = re.sub(r" [0-9A-F]{8}=[0-9A-F]{8}", "", m.group(5)).strip()
            rest = re.sub(r"(hero|twin|sid\d+)\[", "u[", rest)     # the role name needs both pointers; not compared
            d[int(m.group(1))] = (m.group(2), m.group(3), m.group(4), rest)
    return d


a, b = load(sys.argv[1]), load(sys.argv[2])
# a probe line is written only on change: carry the last line forward
def at(d, keys):
    out, cur = {}, None
    ks = sorted(d)
    i = 0
    for f in keys:
        while i < len(ks) and ks[i] <= f:
            cur = d[ks[i]]
            i += 1
        out[f] = cur
    return out

both = sorted(set(a) & set(b))
fa, fb = at(a, both), at(b, both)
bad = [f for f in both if fa[f] != fb[f]]
print("change lines: %d and %d; frames written in both: %d; of these different: %d" % (len(a), len(b), len(both), len(bad)))
for f in bad[:6]:
    print(" ", f, "A:", fa[f][3][:150])
    print(" ", f, "B:", fb[f][3][:150])
