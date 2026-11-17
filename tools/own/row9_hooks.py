"""Read-only (plan row 9, second half): for every decoded boss script that hooks a script onto an object
(trap_obj_hook), say from where each hook is made: from the REACTION_CALLBACK (the answer to a hero's own command)
or from somewhere else (the boss's own acts: a move the boss FORCES). Reads the decoded texts of lane H
(local/analysis/h/ai/B_*.txt). The call graph is the "jal n, Lxxx" lines; a function is a label that some jal
goes to, or a named entry.
  python -I tools/own/row9_hooks.py            -> a table on the screen
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
AI = ROOT / "local" / "analysis" / "h" / "ai"


def study(path):
    L = path.read_text(errors="replace").splitlines()
    lab_at = {}
    for i, l in enumerate(L):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", l)
        if m:
            lab_at.setdefault(m.group(1), i)
    jal_to = set()
    for l in L:
        m = re.search(r"\bjal \d+, (L\d+)", l)
        if m:
            jal_to.add(m.group(1))
    named = [k for k in lab_at if not re.match(r"^[LD]\d+$", k)]
    starts = sorted({lab_at[k] for k in named} | {lab_at[k] for k in jal_to if k in lab_at})
    name_of = {}
    for k in named:
        name_of[lab_at[k]] = k
    for k in jal_to:
        if k in lab_at:
            name_of.setdefault(lab_at[k], k)

    def func_of(i):
        s = max([x for x in starts if x <= i], default=None)
        return name_of.get(s, "?") if s is not None else "?"

    calls = {}
    for i, l in enumerate(L):
        m = re.search(r"\bjal \d+, (L\d+)", l)
        if m:
            calls.setdefault(func_of(i), set()).add(m.group(1))
    reach = set()
    todo = ["REACTION_CALLBACK"] if "REACTION_CALLBACK" in lab_at else []
    while todo:
        f = todo.pop()
        if f in reach:
            continue
        reach.add(f)
        todo.extend(calls.get(f, ()))
    hooks = [i for i, l in enumerate(L) if "trap_obj_hook (" in l]
    out = []
    for i in hooks:
        f = func_of(i)
        fn = L[i - 2].strip().replace("push ", "") if i >= 2 else "?"
        out.append((fn, f, f in reach))
    caps = sum(1 for l in L if "trap_obj_motion_capture (" in l)
    ovr = sum(1 for l in L if "trap_command_override" in l)
    return out, caps, ovr


def main():
    rows = []
    for p in sorted(AI.glob("B_*.txt")):
        hooks, caps, ovr = study(p)
        if not hooks:
            continue
        forced = [h for h in hooks if not h[2]]
        answer = [h for h in hooks if h[2]]
        rows.append((p.stem, len(hooks), len(forced), len(answer), caps, ovr,
                     " ".join("%s@%s" % (h[0], h[1]) for h in forced)[:110]))
    print("%-20s %5s %6s %6s %4s %4s  %s" % ("script", "hooks", "forced", "answer", "caps", "cmds", "forced hooks: function hooked @ where"))
    for r in rows:
        print("%-20s %5d %6d %6d %4d %4d  %s" % r)
    print("%d scripts; with at least one hook that is NOT an answer to a command: %d" % (len(rows), sum(1 for r in rows if r[2])))


if __name__ == "__main__":
    main()
