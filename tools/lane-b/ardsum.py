"""Summarise a room dump made by `Kh2Tool ard-dump`: scripts as they are, spawn groups with object names.

  python -I tools/lane-b/ardsum.py <room> [--groups] [--prog HEX]
room = e.g. hb09 (reads local/analysis-b/ard/hb09.txt and local/analysis/objentry.txt)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
objs = {}
for line in (ROOT / "local" / "analysis" / "objentry.txt").read_text().splitlines():
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = (m.group(2), m.group(3))

room = sys.argv[1]
text = (ROOT / "local" / "analysis-b" / "ard" / f"{room}.txt").read_text()
want_groups = "--groups" in sys.argv
prog = None
if "--prog" in sys.argv:
    prog = sys.argv[sys.argv.index("--prog") + 1].upper()

entries = re.split(r"^==== entry ", text, flags=re.M)[1:]
for e in entries:
    head, _, body = e.partition("\n")
    name = head.split()[0]
    typ = head.split()[2]
    if typ == "AreaDataScript":
        blocks = re.split(r"^(?=Program 0x)", body, flags=re.M)
        for b in blocks:
            if not b.strip():
                continue
            pid = b.split()[1][2:].upper()
            if prog and pid.lstrip("0") != prog.lstrip("0"):
                continue
            print(f"[{name}] " + b.strip().replace("\n", "\n      "))
    elif typ == "AreaDataSpawn" and want_groups:
        ents = re.findall(r"\[(\d+)\] obj 0x([0-9A-F]+) pos \(([^)]*)\) rotY (\S+) type (\d+) arg (\d+)", body)
        if not ents:
            continue
        desc = []
        for idx, oid, pos, rot, st, sa in ents:
            t, mdl = objs.get(int(oid, 16), ("?", "?"))
            desc.append(f"{mdl}({t[:4]},{st}/{sa})")
        sp = len(re.findall(r"spawnpoint \d+:", body))
        print(f"<{name}> {sp} point(s): " + " ".join(desc))
