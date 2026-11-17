"""Read the file pool sweep's logs (tools/own/r9_chain7.sh, probe kb_probe.py): for each mission the least
"free" of its looks, whether the heroes were there, the result; then the tightest rooms.
  python -I tools/own/pool_read.py <log> [<log> ...]"""
import re
import sys

rows = []
for path in sys.argv[1:]:
    for l in open(path, encoding="utf-8", errors="replace"):
        if l.startswith("sweep worker") or "|" not in l:
            continue
        head = l.split("|")[0].split()
        free = [int(x) for x in re.findall(r"\(free (-?\d+)\)", l)]
        heroes = "P1 none P2 none" not in l and "nopic" not in l
        sync = "never out of sync" in l
        tlb = re.search(r"TLB misses (\d+)", l)
        rows.append((min(free) if free else None, " ".join(head[:4]), heroes, sync, int(tlb.group(1)) if tlb else -1,
                     len(re.findall(r"2303", l)) > 0))
print("%d missions; with heroes at the looks: %d; never out of sync: %d; with a pool reading: %d" % (
    len(rows), sum(1 for r in rows if r[2]), sum(1 for r in rows if r[3]), sum(1 for r in rows if r[0] is not None)))
have = sorted([r for r in rows if r[0] is not None])
print("free < 0: %d;  free < 300,000: %d;  free < 1,000,000: %d" % (
    sum(1 for r in have if r[0] < 0), sum(1 for r in have if r[0] < 300000), sum(1 for r in have if r[0] < 1000000)))
for r in have[:14]:
    print("  free %9d  %-34s heroes %s sync %s faults %d" % (r[0], r[1], r[2], r[3], r[4]))
bad = [r for r in rows if not r[3]]
print("not closed in sync: %d" % len(bad))
