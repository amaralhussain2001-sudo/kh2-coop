"""Lane G: list the game's commands (03system.bin CMD table dumped by lane C) with their English names.

  python -I tools/lane-g/cmd_names.py [word ...]        writes local/analysis/g/cmd_names.txt, prints matches
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
A = ROOT / "local" / "analysis" / "lane-c"
names = {}
for line in (A / "sys_en_built.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
    p = line.split("\t")
    if len(p) >= 2:
        names[p[0].strip()] = p[1].strip()
ents = re.split(r"\n- ", "\n" + (A / "cmd.yml").read_text(encoding="utf-8", errors="replace"))
rows = []
for e in ents:
    d = dict(re.findall(r"^\s*(\w+): (.*)$", e, re.M))
    if "Id" not in d:
        continue
    mid = d.get("MessageId", "")
    nm = names.get(mid) or (names.get(str(int(mid) & 0x7FFF)) if mid.isdigit() else "") or ""
    rows.append((int(d["Id"]), nm, d))
out = ROOT / "local" / "analysis" / "g" / "cmd_names.txt"
with open(out, "w", encoding="utf-8") as f:
    for i, nm, d in rows:
        f.write(f"0x{i:04X} {i:4d}  {nm[:40]:40s} exec {d.get('Execute')} arg {d.get('Argument')} sub {d.get('SubMenu')} icon {d.get('CmdIcon')} cost {d.get('Cost')} recv {d.get('CmdReceiver')} flags {d.get('Flags')}\n")
words = [w.lower() for w in sys.argv[1:]]
for i, nm, d in rows:
    if words and any(w in nm.lower() for w in words):
        s = f"0x{i:04X} {nm[:36]:36s} exec {d.get('Execute')} arg {d.get('Argument')} sub {d.get('SubMenu')} icon {d.get('CmdIcon')} cost {d.get('Cost')}"
        print(s.encode("ascii", "replace").decode())
print("commands:", len(rows), "named:", sum(1 for r in rows if r[1]), "->", out)
