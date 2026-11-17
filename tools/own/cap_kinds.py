"""Read-only (ninth round, the user's item 4 of 2026-11-15 evening): from the capture logs of tools/own/cap_log_probe2.py
(local/tests/r9<tag>-*-probe.txt), for each fight: every capture by an enemy (not a hero), grouped by (captor, move): how
often it took player 1's hero, player 2's hero (the sixty-fifth glue's mirror captures, return address inside the glue,
are counted apart), and ANOTHER victim (a party member: Riku, Donald ...) in the same frame (+- 2) with the same move.
A move that the game itself gives to more than one party member at once is a SHARED mechanic; one victim: single-target.
  python -I tools/own/cap_kinds.py [<tag>,...]          (default rs3,h9)"""
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CAP = re.compile(r"^cap c\d+ f(\d+) victim (\S+) move ([0-9A-F]+) captor (\S+) sender (\S+) script (\S+) player (\S+) ra ([0-9A-F]+)")
tags = (sys.argv[1] if len(sys.argv) > 1 else "rs3,h9").split(",")
for tag in tags:
    for f in sorted((ROOT / "local" / "tests").glob("r9%s-*-probe.txt" % tag)):
        caps = []
        for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = CAP.match(l)
            if m:
                caps.append((int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5), int(m.group(8), 16)))
        if not caps:
            continue
        groups = collections.OrderedDict()
        for fr, victim, move, captor, sender, ra in caps:
            if captor in ("P1", "P2"):
                continue
            k = (captor, move)
            g = groups.setdefault(k, collections.Counter())
            mirror = 0x000ECF40 <= ra < 0x000EDC00
            who = victim if victim in ("P1", "P2") else "other"
            g[who + (" (mirror)" if mirror else "")] += 1
            if sender not in ("-", "00000000"):
                g["answer to a command"] += 1
            if who in ("P1", "P2") and not mirror:
                others = [c for c in caps if abs(c[0] - fr) <= 2 and c[2] == move and c[1] not in ("P1", "P2")]
                if others:
                    g["same move to another party member in the same frames"] += 1
        print("== %s" % f.name.replace("-probe.txt", ""))
        for (captor, move), g in groups.items():
            print("   captor %s move %s: %s" % (captor, move, ", ".join("%s %d" % kv for kv in g.items())))
