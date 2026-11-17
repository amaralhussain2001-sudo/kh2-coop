"""Fill the two tick columns of docs/PARITY-CHECKLIST.csv ("checked_with_two_players", "date_checked") from the
mission sweep (docs/PARITY-SWEEP.md, written by tools/own/sweep_doc.py; run that first). A row gets one line:
how many of its mission programs were run by the test script and with which result classes. This is a SCRIPT
check with two linked emulators, not two humans: the text says so. Rows without mission programs are left as
they are. Also appends nothing to the Markdown checklist.
  python -I tools/own/sweep_csv.py [date]        (date default 2026-11-12)"""
import collections
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOCS = ROOT / "docs"
date = sys.argv[1] if len(sys.argv) > 1 else "2026-11-12"
per_row = collections.defaultdict(list)
for line in (DOCS / "PARITY-SWEEP.md").read_text(encoding="utf-8").splitlines():
    c = [x.strip() for x in line.split("|")]
    if len(c) >= 8 and re.fullmatch(r"[A-Z0-9]+-\d+", c[1]):
        per_row[c[1]].append(c[4])
path = DOCS / "PARITY-CHECKLIST.csv"
with open(path, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f))
head = rows[0]
i_id, i_chk, i_date = head.index("id"), head.index("checked_with_two_players"), head.index("date_checked")
n = 0
for r in rows[1:]:
    res = per_row.get(r[i_id])
    if not res:
        continue
    cnt = collections.Counter(x for cell in res for x in cell.split(" + "))
    good = sum(v for k, v in cnt.items() if k in ("OK", "OK-V5", "OK-GAME", "SHARED"))
    r[i_chk] = "script sweep, not humans: %d mission program(s) started with two players; %s (docs/PARITY-SWEEP.md)" % (
        len(res), ", ".join("%s %d" % kv for kv in sorted(cnt.items(), key=lambda kv: -kv[1])))
    r[i_date] = date
    n += 1
with open(path, "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f, lineterminator="\r\n").writerows(rows)
print("rows filled:", n, "of", len(rows) - 1)
