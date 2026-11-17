"""Lane N: short summary of a probe file (tools/lane-n/nprobe.py).

  python -I tools/lane-n/nsum.py <probe.txt> [--all] [--max N] [--from F] [--to F] [--pos]

One line per change of: room, Game Over flag, each hero's HP / fallen flag / action / MP, lane N's down flags and
counters (and the position when --pos is given). Friends are shown only with --all.
"""
import re
import struct
import sys

path = sys.argv[1]
show_all = "--all" in sys.argv
with_pos = "--pos" in sys.argv
mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 80
f_from = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
f_to = int(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else 10 ** 9
last, n = None, 0
for line in open(path, encoding="utf-8"):
    if line.startswith(("params", "battle")) or "WRITE" in line:
        print(line.rstrip()[:200])
        continue
    m = re.match(r"\s*(\d+) room (\w+) btl (\d) go (\d) nvars ((?:\w{8} ?){6,8})\| (.*)", line)
    if not m:
        continue
    f, room, btl, go, nv, rest = m.groups()
    if not f_from <= int(f) <= f_to:
        continue
    nvw = [int(x, 16) for x in nv.split()]
    t0 = struct.unpack("<f", struct.pack("<I", nvw[0]))[0]
    t1 = struct.unpack("<f", struct.pack("<I", nvw[1]))[0]
    units = re.findall(r"(\w+)\[(\w+)(\*?)\] (-?\d+)/(\d+) mp (-?\d+) obj (\w+) fl (\w+) act (\w+)(?: t (-?[\d.]+))?(?: @(-?\d+),(-?\d+),(-?\d+))?", rest)
    key, txt = [room, go] + nvw[2:], []
    for role, slot, mark, hp, mhp, mp, obj, fl, act, tm, px, py, pz in units:
        if not show_all and role not in ("hero", "twin"):
            continue
        dead = int(fl, 16) & 4
        pos = (" @%s,%s,%s" % (px, py, pz)) if (with_pos and px) else ""
        key.append((role, hp, dead, act, mp, pos))
        txt.append("%s %s/%s mp %s %s act %s%s%s" % (role, hp, mhp, mp, "DOWN" if dead else "up", act,
                                                      (" t %s" % tm) if tm else "", pos))
    if key != last:
        last = key
        n += 1
        if n <= mx:
            print("%6s room %s btl %s go %s down %d/%d falls %d/%d rev %d/%d T %.0f/%.0f | %s" % (
                f, room, btl, go, nvw[2], nvw[3], nvw[4], nvw[5], nvw[6] if len(nvw) > 6 else 0, nvw[7] if len(nvw) > 7 else 0, t0, t1, " | ".join(txt)))
print("(%d change lines)" % n)
