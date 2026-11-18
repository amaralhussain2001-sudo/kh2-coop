"""Read a snd_probe.py output: for every 3D sound (kind 0 or 5, state 2) compare its volume with what camera 1 and camera 2 would
give (16383 - distance^2 / K, K measured 500 in the control r15sc) and say which camera it matches.
  python -I tools/own/snd_check.py <probe.txt> [K]
"""
import re
import sys

K = float(sys.argv[2]) if len(sys.argv) > 2 else 500.0
V = re.compile(r"\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)")
eyes = {}
count = {"cam1": 0, "cam2": 0, "both": 0, "neither": 0}
louder_lost = 0
for line in open(sys.argv[1], encoding="utf-8"):
    f = line.split()[0]
    if " hero " in line:
        vs = [tuple(map(float, m)) for m in V.findall(line)]
        eyes[f] = (vs[-2], vs[-1])
        continue
    if " node " not in line or f not in eyes:
        continue
    m = re.search(r"pos \(([-\d.]+) ([-\d.]+) ([-\d.]+)\).* vol (-?\d+) low (-?\d+) pan (-?\d+) .* state (\d+) kind (\d+)", line)
    if not m:
        continue
    x, y, z, vol, low, pan, state, kind = float(m[1]), float(m[2]), float(m[3]), int(m[4]), int(m[5]), int(m[6]), int(m[7]), int(m[8])
    if kind not in (0, 5) or state != 2:
        continue
    exp = []
    for e in eyes[f]:
        d2 = (x - e[0]) ** 2 + (y - e[1]) ** 2 + (z - e[2]) ** 2
        exp.append(max(low, max(0, int(16383 - d2 / K))))
    near1, near2 = abs(vol - exp[0]) <= 60, abs(vol - exp[1]) <= 60
    tag = "both" if near1 and near2 else "cam1" if near1 else "cam2" if near2 else "neither"
    count[tag] += 1
    if max(exp) - vol > 300:
        louder_lost += 1
    print("%s pos (%.0f %.0f %.0f) vol %5d  cam1 %5d cam2 %5d -> %s" % (f, x, y, z, vol, exp[0], exp[1], tag))
print("SUMMARY", count, "| sounds quieter than the nearer camera would give (by > 300):", louder_lost)
