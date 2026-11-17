"""Read-only: room programs that give the party friends, play no event and have no battle program of the same
number (candidates for a quiet test room with helpers). Reads the text dumps in local/analysis/ard-all."""
import collections
import pathlib
import re

D = pathlib.Path(__file__).resolve().parent.parent.parent / "local" / "analysis" / "ard-all"
progs = {}          # (room, entry) -> {number: [lines]}
for f in sorted(D.glob("*.txt")):
    entry = None
    cur = None
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
        if m:
            entry = m.group(1) if m.group(2) == "AreaDataScript" else None
            cur = None
            continue
        if entry is None:
            continue
        m = re.match(r"Program (0x[0-9A-Fa-f]+)", line)
        if m:
            cur = progs.setdefault((f.stem, entry), {}).setdefault(int(m.group(1), 16), [])
            continue
        if cur is not None and line.strip():
            cur.append(line.strip())
count = collections.Counter()
for (room, entry), ps in progs.items():
    if entry == "evt":
        for n in ps:
            count[(room[:2], n)] += 1
for (room, entry), ps in sorted(progs.items()):
    if entry != "evt":
        continue
    for n, lines in sorted(ps.items()):
        party = [l for l in lines if l.startswith("Party")]
        if not party or party[0] == "Party NO_FRIEND":
            continue
        if any(l.startswith("SetEvent") or l.startswith("SetJump") for l in lines):
            continue
        btl = progs.get((room, "btl"), {}).get(n)
        if btl:
            continue
        if count[(room[:2], n)] != 1:
            continue
        print(room, "program 0x%02X (%d)" % (n, n), "|", "; ".join(lines)[:150], "| map:", "; ".join(progs.get((room, "map"), {}).get(n, ["-"]))[:80])
