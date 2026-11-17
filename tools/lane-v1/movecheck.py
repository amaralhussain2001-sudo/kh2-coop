"""Lane K: from a camprobe output file, compare the twin's (or hero's) movement direction between two frames with
each camera's forward direction.   python -I movecheck.py <camprobe.txt> <frameA> <frameB> [hero|twin]"""
import math
import re
import sys

t = open(sys.argv[1]).read()
fa, fb = int(sys.argv[2]), int(sys.argv[3])
who = sys.argv[4] if len(sys.argv) > 4 else "twin"
d = {}
num = r"\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\)"
for b in t.split("frame ")[1:]:
    f = int(b.split(":")[0])
    m = re.search(who + r" 0x\w+ pos " + num, b)
    cams = re.findall(r"(cam\d) eye " + num + r" at .*? p10 " + num, b)
    d[f] = (tuple(map(float, m.groups())), {c[0]: (tuple(map(float, c[1:4])), tuple(map(float, c[4:7]))) for c in cams})


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n) if n else (0.0, 0.0)


mv = (d[fb][0][0] - d[fa][0][0], d[fb][0][2] - d[fa][0][2])
print("%s moved (x, z): %.1f %.1f" % ((who,) + mv))
for c in ("cam1", "cam2"):
    look, eye = d[fa][1][c]
    fw = unit((look[0] - eye[0], look[2] - eye[2]))
    m = unit(mv)
    print("%s forward (x, z): %.2f %.2f   cosine with the movement: %.2f" % (c, fw[0], fw[1], fw[0] * m[0] + fw[1] * m[1]))
