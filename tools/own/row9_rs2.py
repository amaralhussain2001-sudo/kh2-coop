"""Read-only (ninth round, job 3): sum up the 40 "RUN / SWEEP" fights of docs/ROW9-PAIRED-MOVES.md as they were played on
purpose with two heroes on the candidate of build 20 (v115: tools/own/r9_chain47.sh, tag rs3; on v112 before:
r9_chain43.sh, tag rs2; capture log, HP held,
20,000 frames, both players Circle / Triangle / R1). For each fight: the session's result and fault line count
(from the logs local/sweep/r9/rs2*.log), each hero's held stretches and the sixty-fifth glue's pairs (from the
timeline local/tests/r9rs2-<MISSION>-<program>-probe.txt, read as tools/own/holdstat.py reads it).
The same for the ten boss rooms of tools/own/r9_chain17.sh on the same candidate (tag h9), when they are there.
  python -I tools/own/row9_rs2.py [--json] [--tags=rs2,h9]     (--json: the table for tools/own/row9_report.py)"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
TAGS = ["rs3", "h9"]          # the candidate of build 20 (v115): the 40 fights (r9_chain47.sh), the ten boss rooms (r9_chain46.sh)
for _a in sys.argv[1:]:
    if _a.startswith("--tags="):
        TAGS = _a[7:].split(",")
TESTS = ROOT / "local" / "tests"
ACT = re.compile(r"^act f(\d+) P1 a([0-9A-F]+) held (\d) hook (\d) \(([^)]*)\) \| P2 a([0-9A-F]+) held (\d) hook (\d) \(([^)]*)\)")
PAIR = re.compile(r"^pair f(\d+) (\S+) (\S+) captor (\S+) named (\S+)")
HEAD = re.compile(r"^(\w+) (\w+) (\d+) (\w+) (\w+) \| (.*?) \| p1 TLB misses (\d+)")


def held(rows, who):
    """-> (count, longest stretch, longest stretch in one action)"""
    n, longest, one, start, act, act_start = 0, 0, 0, None, None, None
    last = rows[-1][0] if rows else 0
    for r in rows + [(last, "00", 0, 0, "00", 0, 0)]:
        a, h = (r[1], r[2]) if who == 1 else (r[4], r[5])
        if h:
            if start is None:
                start, n = r[0], n + 1
                act, act_start = a, r[0]
            elif a != act:
                one = max(one, r[0] - act_start)
                act, act_start = a, r[0]
        elif start is not None:
            longest = max(longest, r[0] - start)
            one = max(one, r[0] - act_start)
            start = None
    return n, longest, one


def main():
    out = []
    for tag, log in [(t, l) for t in TAGS for l in sorted((ROOT / "local" / "sweep" / "r9").glob(t + "[0-9].log"))]:
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = HEAD.match(line)
            if not m:
                continue
            room, _world, prog, mission, _friend, result, tlb = m.groups()
            probe = TESTS / ("r9%s-%s-%s-probe.txt" % (tag, mission, prog))
            rows, pairs, cur = [], [], None
            if probe.exists():
                for l in probe.read_text(encoding="utf-8", errors="replace").splitlines():
                    a = ACT.match(l)
                    if a:
                        rows.append((int(a.group(1)), a.group(2), int(a.group(3)), int(a.group(4)),
                                     a.group(6), int(a.group(7)), int(a.group(8))))
                        continue
                    q = PAIR.match(l)
                    if q:
                        f = int(q.group(1))
                        if q.group(2) != "-" and cur is None:
                            cur = f
                        elif q.group(2) == "-" and cur is not None:
                            pairs.append(f - cur)
                            cur = None
            sync = "never out of sync" in result
            m2 = re.search(r"closed at frame (\d+)", result)
            p1, p2 = held(rows, 1), held(rows, 2)
            out.append({"tag": tag, "room": room, "program": int(prog), "mission": mission, "sync": sync, "result": result[:90],
                        "end": int(m2.group(1)) if m2 else 0, "tlb": int(tlb), "p1": p1, "p2": p2,
                        "pairs": len(pairs), "pair_longest": max(pairs) if pairs else 0,
                        "last_frame": rows[-1][0] if rows else 0, "open_pair": cur is not None})
    if "--json" in sys.argv:
        print(json.dumps(out))
        return
    bad = 0
    for o in out:
        flag = "" if o["sync"] and o["tlb"] == 0 else "  <-- LOOK"
        if max(o["p1"][2], o["p2"][2]) >= 1500:
            flag += "  <-- LONG HOLD"
        bad += 1 if flag else 0
        print("%-5s %3d %-12s %s TLB %d | P1 held %d (longest %d, one action %d) | P2 held %d (longest %d, one action %d) | pairs %d (longest %d)%s" % (
            o["room"], o["program"], o["mission"], "in sync" if o["sync"] else "NOT: " + o["result"], o["tlb"],
            o["p1"][0], o["p1"][1], o["p1"][2], o["p2"][0], o["p2"][1], o["p2"][2], o["pairs"], o["pair_longest"], flag))
    print("%d fights read, %d to look at" % (len(out), bad))


main()
