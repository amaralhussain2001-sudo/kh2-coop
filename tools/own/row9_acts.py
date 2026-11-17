"""Read-only (plan row 9, second half; ninth round): ONE BOSS'S FORCED MOVE AS A LIST OF ENGINE CALLS. For a decoded
boss script (local/analysis/h/ai/<NAME>.txt) and a range of its lines or labels, print only the labels, the
script's own calls (jal), the branches back (loops), the "halt" (= wait one step) and every engine call (syscall)
with the constants pushed just before it. So a grab reads as: attach(.., bone 71) / capture 252 / wait / ...
  python -I tools/own/row9_acts.py <NAME> <fromLabelOrLine> <toLabelOrLine>
  python -I tools/own/row9_acts.py <NAME> --hooks         every trap_obj_hook: the function that makes it and the hooked one
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
name = sys.argv[1]
L = (ROOT / "local" / "analysis" / "h" / "ai" / (name + ".txt")).read_text(errors="replace").splitlines()
lab = {}
for i, l in enumerate(L):
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", l)
    if m:
        lab.setdefault(m.group(1), i)


def where(x):
    return lab[x] if x in lab else int(x) - 1


def show(a, b):
    consts = []
    for i in range(a, min(b, len(L))):
        l = L[i].strip()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", l)
        if m:
            print("%s:" % m.group(1))
            consts = []
            continue
        m = re.match(r"push(?:\.s)? (-?[\d.]+)$", l)
        if m:
            consts.append(m.group(1))
            continue
        if l.startswith("syscall"):
            t = l.split(";")[1].strip() if ";" in l else l
            print("   %5d  %s   <- %s" % (i + 1, t.split(" (")[0], " ".join(consts[-6:])))
            consts = []
        elif l.startswith("jal ") or l == "halt" or l == "ret" or re.match(r"b L\d+", l) or l.startswith("push.bd") or l.startswith("push.wp") or l.startswith("pop.wp"):
            print("   %5d  %s" % (i + 1, l))
            if not l.startswith("push"):
                consts = []
        elif not l.startswith("push"):
            pass


if sys.argv[2] == "--hooks":
    for i, l in enumerate(L):
        if "trap_obj_hook" in l:
            fn = None
            for j in range(i - 1, max(i - 8, 0), -1):
                m = re.match(r"\s*push (\d+)$", L[j])
                if m and int(m.group(1)) > 50:
                    fn = "L" + m.group(1)
                    break
            st = max([v for k, v in lab.items() if v <= i and not re.match(r"^D\d+$", k)], default=0)
            print("hook at line %d: hooked function %s; made in the block that starts at line %d (%s)" % (
                i + 1, fn, st + 1, [k for k, v in lab.items() if v == st][0]))
else:
    show(where(sys.argv[2]), where(sys.argv[3]) + 1)
