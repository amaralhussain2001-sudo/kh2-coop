"""Read-only (ninth round, the user's item 2 of 2026-11-15 evening: Shan-Yu's stray calls): from a capture log of
tools/own/cap_log_probe2.py in Shan-Yu's room, each hero's clash stretches (from his FC to his FE / 100) and every capture
of a hero OUTSIDE his own stretch (a "stray call": the old fault of builds 13 / 14, part 38) or made by another captor.
  python -I tools/own/sy_stray.py <probe.txt> [...]"""
import re
import sys

CAP = re.compile(r"^cap c(\d+) f(\d+) victim (\S+) move ([0-9A-F]+) captor (\S+) sender (\S+) script (\S+) player (\S+) ra ([0-9A-F]+)")
for fn in sys.argv[1:]:
    caps = [m.groups() for m in (CAP.match(l) for l in open(fn, encoding="utf-8", errors="replace")) if m]
    print("==", fn.split("/")[-1].split("\\")[-1], len(caps), "captures")
    open_at, stretches, stray = {}, [], []
    for c, f, v, mv, cap, snd, scr, pl, ra in caps:
        if v not in ("P1", "P2"):
            continue
        mv = int(mv, 16)
        if mv == 0xFC and v not in open_at:
            open_at[v] = (int(c), cap, 0)
            continue
        if v not in open_at:
            stray.append((c, f, v, "%02X" % mv, cap, ra))
            continue
        st, cap0, n = open_at[v]
        if cap != cap0:
            stray.append((c, f, v, "%02X" % mv, cap, ra))
        if mv == 0xFF:
            open_at[v] = (st, cap0, n + 1)
        if mv in (0xFE, 0x100):
            stretches.append((v, st, int(c), n + (1 if mv == 0xFF else 0), "%02X" % mv))
            del open_at[v]
    for v, st, en, n, how in stretches:
        print("  clash %s counter %d .. %d (%d steps): %d pushes (FF), ends %s" % (v, st, en, en - st, n, how))
    for v, (st, cap0, n) in open_at.items():
        print("  clash %s from %d still open at the end (%d pushes)" % (v, st, n))
    print("  captures outside a hero's own clash stretch (stray):", len(stray))
    for s in stray[:12]:
        print("   ", " ".join(s))
