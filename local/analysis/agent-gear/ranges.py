import sys, re
p = sys.argv[1]
addrs = []
for line in open(p, encoding="utf-8", errors="replace"):
    m = re.match(r"^([0-9A-F]{8}) ([0-9A-F]{8})\s+(.*)$", line.strip())
    if m:
        addrs.append((int(m.group(1), 16), m.group(3)))
addrs.sort()
blocks = []
for a, d in addrs:
    if blocks and a <= blocks[-1][1] + 4 + 0x40:
        blocks[-1][1] = a
        if d not in blocks[-1][2]: blocks[-1][2].append(d)
    else:
        blocks.append([a, a, [d]])
lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xFFFFFFFF
for b in blocks:
    if b[1] >= lo and b[0] <= hi:
        print("%08X..%08X  %s" % (b[0], b[1] + 3, "; ".join(x[:50] for x in b[2][:3])))
