import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
addrs = []
for raw in p.read_text(encoding="utf-8").splitlines():
    parts = raw.split(None, 2)
    if len(parts) >= 2 and re.fullmatch(r"[0-9A-Fa-f]{8}", parts[0]) and re.fullmatch(r"[0-9A-Fa-f]{8}", parts[1]):
        addrs.append((int(parts[0],16), parts[2] if len(parts)>2 else ""))
addrs.sort()
lo = int(sys.argv[2],16) if len(sys.argv)>2 else 0
hi = int(sys.argv[3],16) if len(sys.argv)>3 else 0xFFFFFFFF
runs = []
for a, o in addrs:
    if not (lo <= a < hi): continue
    if runs and a == runs[-1][1] + 4 and (o.split('(')[0][:40] == runs[-1][2].split('(')[0][:40] or True):
        runs[-1][1] = a
        if o[:50] != runs[-1][2][:50] and o[:50] not in runs[-1][3]: runs[-1][3].append(o[:50])
    else:
        runs.append([a, a, o, []])
for s, e, o, more in runs:
    print("%08X-%08X %5d  %s %s" % (s, e+3, (e-s)//4+1, o[:70], ("| +" + str(len(more))) if more else ""))
