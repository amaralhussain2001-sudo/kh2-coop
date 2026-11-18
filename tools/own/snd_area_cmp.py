"""Compare AREA sounds (kind 4) of two snd_probe.py outputs (control, candidate) frame by frame, node by node.
For each: the volume, the point, its squared distance to each eye (in units of K=500: 16383 - that = the volume each camera gives).
  python -I tools/own/snd_area_cmp.py <control-probe.txt> <candidate-probe.txt>
"""
import re
import sys

V = re.compile(r"\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)")
N = re.compile(r"^(f\d+)  node (\w+) pos \(([-\d.]+) ([-\d.]+) ([-\d.]+)\) .* vol (-?\d+) low (-?\d+) pan (-?\d+) .* state (\d+) kind (\d+)")


def load(path):
    eyes, nodes = {}, {}
    for line in open(path, encoding="utf-8"):
        f = line.split()[0]
        if " hero " in line:
            vs = [tuple(map(float, m)) for m in V.findall(line)]
            eyes[f] = (vs[-2], vs[-1])
            continue
        m = N.match(line)
        if m and m[10] == "4":
            nodes.setdefault(f, {})[m[2]] = (float(m[3]), float(m[4]), float(m[5]), int(m[6]), int(m[8]))
    return eyes, nodes


def cam_vol(p, e):
    d2 = sum((a - b) ** 2 for a, b in zip(p[:3], e))
    return max(0, int(16383 - d2 / 500.0))


ce, cn = load(sys.argv[1])
ne, nn = load(sys.argv[2])
louder = same = quieter = 0
for f in sorted(cn, key=lambda x: int(x[1:])):
    for addr in sorted(cn[f]):
        c = cn[f][addr]
        n = nn.get(f, {}).get(addr)
        if n is None:
            continue
        e0, e1 = ne[f]
        tag = "same" if abs(n[3] - c[3]) <= 60 else "LOUDER" if n[3] > c[3] else "quieter"
        louder += tag == "LOUDER"
        same += tag == "same"
        quieter += tag == "quieter"
        print("%s %s control vol %5d pt (%.0f %.0f %.0f) | candidate vol %5d pt (%.0f %.0f %.0f) cam1 %5d cam2 %5d -> %s" % (
            f, addr, c[3], c[0], c[1], c[2], n[3], n[0], n[1], n[2], cam_vol(n, e0), cam_vol(n, e1), tag))
print("SUMMARY louder %d same %d quieter %d" % (louder, same, quieter))
