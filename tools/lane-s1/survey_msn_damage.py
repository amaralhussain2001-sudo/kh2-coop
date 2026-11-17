"""Survey of the decoded mission scripts: which have an OBJ_DAMAGE trigger and what the handler asks.

  python -I tools/lane-s1/survey_msn_damage.py <dirWithDecodedTexts>

For each script with an OBJ_DAMAGE trigger: the traps reached from the handler (following jal inside the script).
"""
import pathlib
import re
import sys

d = pathlib.Path(sys.argv[1])
rows = []
for f in sorted(d.glob("*_0.txt")):
    lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
    name = ""
    for l in lines[:30]:
        if l.startswith("Name:"):
            name = l.split(":", 1)[1].strip()
    labels = {}
    for i, l in enumerate(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$", l)
        if m:
            labels[m.group(1)] = i
    all_traps = re.findall(r"; (trap_\w+|method_\w+)", "\n".join(lines))
    if "OBJ_DAMAGE" not in labels:
        rows.append((f.stem, name, None, all_traps))
        continue
    seen, todo, traps = set(), ["OBJ_DAMAGE"], []
    while todo:
        lab = todo.pop()
        if lab in seen or lab not in labels:
            continue
        seen.add(lab)
        i = labels[lab] + 1
        while i < len(lines):
            l = lines[i].strip()
            m = re.match(r"^(jal|b|beqz|bnez|blez|bgtz|bltz|bgez)\b.*?\b(L\d+)$", l)
            if m:
                todo.append(m.group(2))
            m = re.search(r"; (trap_\w+|method_\w+)", l)
            if m:
                traps.append(m.group(1))
            if l == "ret" or l.startswith("halt"):
                break
            i += 1
    rows.append((f.stem, name, traps, all_traps))

with_dmg = [r for r in rows if r[2] is not None]
print("scripts:", len(rows), "with OBJ_DAMAGE:", len(with_dmg))
for stem, name, traps, _all in with_dmg:
    print("%-22s %-22s %s" % (stem, name, " ".join(sorted(set(traps)))))
print()
print("scripts that call trap_sysobj_player anywhere:")
for stem, name, traps, all_traps in rows:
    if "trap_sysobj_player" in all_traps:
        print("  %-22s %-22s x%d  cmp x%d  is_player x%d" % (stem, name, all_traps.count("trap_sysobj_player"),
              all_traps.count("trap_obj_cmp"), all_traps.count("trap_sysobj_is_player")))
