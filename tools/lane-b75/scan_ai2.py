"""Resolve which enemy-table entries (ENMP ids) each object's AI script can give the object.

Three cases are handled (see docs/lanes/B75-boss-hp.md):
  A. the id is a constant pushed right before `trap_btlobj_set_sheet`;
  B. the call sits in a set-up routine and the id is one of the routine's parameters: every `jal` to that routine is
     looked at, and the matching pushed argument is taken (a constant, or a local variable);
  C. a local variable: every `push N` + `pop.sp K` (or pop.sp.d K) of that variable in the script is a candidate.
Anything else is reported as unresolved.

  python -I tools/lane-b75/scan_ai2.py <aiDir> <objentry.txt> <enmp.bin> <out.json> <out.tsv>
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from enmp_lib import parse  # noqa: E402

aidir, objtxt, enmpbin, outjson, outtsv = sys.argv[1:6]
ver, entries = parse(open(enmpbin, "rb").read())
VALID = {e["id"] for e in entries}

pat = re.compile(r"^0x([0-9A-F]+) type (\S+)\s+model (\S+)\s+anim (\S*)\s+flags 0x([0-9A-F]+) status (\d+)")
objs = collections.defaultdict(list)
for line in open(objtxt, encoding="utf-8", errors="replace"):
    m = pat.match(line)
    if m:
        objs[m.group(3)].append({"obj": int(m.group(1), 16), "type": m.group(2), "status": int(m.group(6))})

RE_PUSH_INT = re.compile(r"^push (-?\d+)$")
RE_PUSH_VAR = re.compile(r"^push\.d\.sp (\d+)$")
RE_POP = re.compile(r"^pop\.sp(?:\.d)? (\d+)$")
RE_LABEL = re.compile(r"^(L\d+):$")
RE_JAL = re.compile(r"^jal(?:32)? \d+, (L\d+)$")
IS_PUSH = re.compile(r"^push")


def var_candidates(lines, var, lo, hi):
    """Constants stored into local variable `var` between lines lo..hi (same routine)."""
    out = set()
    for i in range(max(lo, 1), hi):
        m = RE_POP.match(lines[i])
        if m and int(m.group(1)) == var:
            p = RE_PUSH_INT.match(lines[i - 1])
            if p:
                out.add(int(p.group(1)))
            else:
                out.add(None)
    return out


def routine_bounds(lines, labels_sorted, i):
    """Nearest label above line i whose body starts with parameter pops, and the next such label."""
    start = 0
    for li in labels_sorted:
        if li <= i:
            start = li
        else:
            break
    nxt = len(lines)
    for li in labels_sorted:
        if li > i:
            nxt = li
            break
    return start, nxt


def analyse(lines):
    lines = [l.strip() for l in lines]
    label_at = {}
    for i, l in enumerate(lines):
        m = RE_LABEL.match(l)
        if m:
            label_at[m.group(1)] = i
    labels_sorted = sorted(label_at.values())
    jals = collections.defaultdict(list)
    for i, l in enumerate(lines):
        m = RE_JAL.match(l)
        if m:
            jals[m.group(1)].append(i)
    ids, unresolved = set(), []
    for i, l in enumerate(lines):
        if "trap_btlobj_dup_sheet" in l:      # (object, id): the shared-slot form
            m = RE_PUSH_INT.match(lines[i - 1])
            if m:
                ids.add(int(m.group(1)))
            else:
                unresolved.append((i, "dup_sheet argument is not a constant: " + lines[i - 1]))
            continue
        if "trap_btlobj_set_sheet" not in l:
            continue
        arg = lines[i - 2]
        m = RE_PUSH_INT.match(arg)
        if m:
            ids.add(int(m.group(1)))
            continue
        m = RE_PUSH_VAR.match(arg)
        if not m:
            unresolved.append((i, "argument is an expression: " + arg))
            continue
        var = int(m.group(1))
        start, nxt = routine_bounds(lines, labels_sorted, i)
        # parameter pops directly after the routine's label
        pops, j = [], start + 1
        while j < len(lines) and RE_POP.match(lines[j]):
            pops.append(int(RE_POP.match(lines[j]).group(1)))
            j += 1
        label = lines[start][:-1] if RE_LABEL.match(lines[start]) else None
        if var in pops and label and jals.get(label):
            n = len(pops)
            k = pops.index(var)          # k-th pop takes the k-th value from the top of the stack
            for site in jals[label]:
                pushes, q = [], site - 1
                while q >= 0 and len(pushes) < n and IS_PUSH.match(lines[q]):
                    pushes.append((q, lines[q]))
                    q -= 1
                if len(pushes) < n:
                    unresolved.append((site, "call to %s: fewer than %d plain pushes before it" % (label, n)))
                    continue
                qline, text = pushes[k]
                mi = RE_PUSH_INT.match(text)
                if mi:
                    ids.add(int(mi.group(1)))
                    continue
                mv = RE_PUSH_VAR.match(text)
                if mv:
                    lo = site
                    while lo > 0 and lines[lo] != "ret":
                        lo -= 1
                    cands = var_candidates(lines, int(mv.group(1)), lo, site)
                    good = {c for c in cands if c is not None}
                    ids |= good
                    if None in cands or not good:
                        unresolved.append((site, "call to %s: id comes from variable %s, not only constants" % (label, mv.group(1))))
                else:
                    unresolved.append((site, "call to %s: id argument is %s" % (label, text)))
        else:
            lo = i
            while lo > 0 and lines[lo] != "ret":
                lo -= 1
            cands = var_candidates(lines, var, lo, i)
            good = {c for c in cands if c is not None}
            ids |= good
            if None in cands or not good:
                unresolved.append((i, "id comes from variable %d (%s)" % (var, "a parameter, no caller found" if var in pops else "not only constants")))
    return ids, unresolved


res = {}
for fn in sorted(os.listdir(aidir)):
    if not fn.endswith(".txt"):
        continue
    model = fn[:-4]
    lines = open(os.path.join(aidir, fn), encoding="utf-8", errors="replace").read().split("\n")
    if not any(("trap_btlobj_set_sheet" in l or "trap_btlobj_dup_sheet" in l) for l in lines):
        continue
    ids, unresolved = analyse(lines)
    res[model] = {"ids": sorted(ids), "valid": sorted(i for i in ids if i in VALID),
                  "not_in_table": sorted(i for i in ids if i not in VALID and i != -1),
                  "unresolved": [u[1] + " (line %d)" % (u[0] + 1) for u in unresolved],
                  "types": sorted({x["type"] for x in objs.get(model, [])}),
                  "objects": ["0x%X" % x["obj"] for x in objs.get(model, [])],
                  "status": sorted({x["status"] for x in objs.get(model, [])})}

json.dump(res, open(outjson, "w", encoding="utf-8"), indent=1)
with open(outtsv, "w", encoding="utf-8") as f:
    f.write("model\ttypes\tobjects\tstatus\tentry_ids\tnot_in_table\tunresolved\n")
    for model in sorted(res):
        r = res[model]
        f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (model, ",".join(r["types"]), " ".join(r["objects"]),
                " ".join(map(str, r["status"])), " ".join(map(str, r["valid"])), " ".join(map(str, r["not_in_table"])),
                " | ".join(r["unresolved"])))
tot = len(res)
clean = sum(1 for r in res.values() if r["valid"] and not r["unresolved"])
print("scripts that set an entry:", tot, "| fully resolved:", clean, "| with something unresolved:",
      sum(1 for r in res.values() if r["unresolved"]), "| no id found at all:", sum(1 for r in res.values() if not r["valid"]))
