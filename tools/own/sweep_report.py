"""Read the mission sweep's logs (local/sweep/*.log, written by tools/own/sweep.sh and sweep1.sh) and sort every
mission into classes. One line per mission; the last word of a log line wins (a rerun replaces the older line).
  python -I tools/own/sweep_report.py [--all] [--md]
Classes:
  OK        in sync, 0 fault lines, the right room, both heroes seen
  P2-NONE   player 1's hero is there, player 2 has no hero at any snapshot
  NO-HERO   the right room, but no hero at any snapshot (a scene, or the mission never started)
  WRONG-ROOM the jump did not arrive in the mission's room at the first snapshot
  FAULT     fault lines (TLB misses) > 0
  DESYNC    the two PCs went out of sync
  NO-END    the session did not close (stopped, crashed or timed out)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
WORLD = {"tt": 2, "hb": 4, "bb": 5, "he": 6, "al": 7, "mu": 8, "po": 9, "lk": 10, "lm": 11, "dc": 12, "wi": 13,
         "nm": 14, "wm": 15, "ca": 16, "tr": 17, "eh": 18, "es": 1, "zz": 0, "dh": 3}
rows = {}
order = []
for log in sorted(SW.glob("*.log")):
    for line in log.read_bytes().decode("utf-8", "replace").replace(chr(13) + " | ", " | ").splitlines():   # (a list file with CR LF leaves a CR behind the party word)
        parts = line.split(" | ")
        head = parts[0].split()
        if len(head) < 5 or len(parts) < 3:
            continue
        key = tuple(head[:3])
        if key not in rows:
            order.append(key)
        rows[key] = (head, parts, log.name)

want = {}
for line in (SW / "missions.txt").read_text(encoding="utf-8").splitlines():
    h = line.split()
    if len(h) >= 5:
        want[tuple(h[:3])] = h

out = []
count = {}
for key in want:
    if key not in rows:
        continue
    head, parts, log = rows[key]
    room, _w, prog, name, party = head[:5]
    res = parts[1]
    tlb = re.search(r"TLB misses (\d+)", " | ".join(parts))
    tlb = int(tlb.group(1)) if tlb else -1
    probe = parts[-1]
    snaps = re.findall(r"f(\d+) room ([0-9A-F]{4}) btl (\d+) L(\d) P1 (none|noslot|\d+/\d+ a[0-9A-F]+) P2 (none|noslot|\d+/\d+ a[0-9A-F]+) msn (\d) go (\d)", probe)
    exp = "%02X%02X" % (int(room[2:]), WORLD.get(room[:2], 0xFF))
    cls = []
    if "never out of sync" not in res:
        cls.append("DESYNC" if "out of sync" in res or "DESYNC" in res.upper() else "NO-END")
    if tlb > 0:
        cls.append("FAULT")
    if not snaps:
        cls.append("NO-PROBE")
    else:
        if snaps[0][1] != exp:
            cls.append("WRONG-ROOM")
        p1 = any(s[4] not in ("none", "noslot") for s in snaps)
        p2 = any(s[5] not in ("none", "noslot") for s in snaps)
        if not p1:
            cls.append("NO-HERO")
        elif not p2:
            cls.append("P2-NONE")
    if not cls:
        cls = ["OK"]
    for c in cls:
        count[c] = count.get(c, 0) + 1
    short = " ; ".join("f%s %s b%s L%s %s|%s m%s g%s" % s for s in snaps)
    out.append((cls, "%-5s %3s %-22s %-12s %-18s tlb %-3d %s" % (room, prog, name, party, "+".join(cls), tlb, short)))

print("missions in the list: %d, with a result: %d" % (len(want), len(out)))
print("  ".join("%s %d" % kv for kv in sorted(count.items())))
for cls, line in out:
    if "--all" in sys.argv or cls != ["OK"]:
        print(line)
