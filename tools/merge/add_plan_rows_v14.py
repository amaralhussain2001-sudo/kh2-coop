"""One-off: KH2-COOP-PLAN.md, a correction at the end of the rows 9 and 53 after the 40 fights on build 21's file (v129, tag rs5)
and their captors (runs ob1 .. ob3; docs/STATE.md part 117). Run once:  python -I tools/merge/add_plan_rows_v14.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "BUILD 21's FILE (v129)" in t:
    raise SystemExit("already there")
ADD = {
    "| 9 |": (" **CORRECTION 2026-11-16 (the 40 fights on BUILD 21's FILE (v129), tag rs5, and runs ob1 .. ob3 with the captors' kinds): "
              "besides the laser dome, the moves of things that are NO ENEMY take both heroes as in build 20 (the Storm Rider fight's "
              "whirlwinds F_MU070_BOSS, kind G_OBJ; moving parts of The World That Never Was F_EH070 / F_EH080 / F_EH110, kind F_OBJ; the "
              "skateboards, Mail Delivery). Every enemy's grab (BOSS, ZAKO, L_BOSS, E_OBJ ...) took only its target. 40 of 40 in sync.** |"),
    "| 53 |": (" **Package of build 21: aa9b18abfa09 (2026-11-16 00:03; the read-me corrected for the shared moves; the game files are "
               "those of e24a7e8821cf, both rehearsed).** |"),
}
lines = t.split("\n")
done = set()
for i, l in enumerate(lines):
    for k, text in ADD.items():
        if l.startswith(k) and k not in done:
            assert l.rstrip().endswith("|")
            lines[i] = l.rstrip()[:-1].rstrip() + text
            done.add(k)
assert done == set(ADD), done
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: rows 9 and 53 corrected")
