"""One-off: tidy part 6 of "Merge 6 and test build 4" in docs/STATE.md after part 8 was added, and add plan row 14."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
a = t.index("Started and not finished: the Grandstander job")
b = t.index("\n\n", a)
t = t[:a] + ("(The states above are the ones before the lock-on fix; the package of that state had the id 172b2f8e8001\n"
             "and was replaced. The validation of the final six-change patches and of package 538e811e10f7 is at the end\n"
             "of part 8. The Grandstander job: part 8.)") + t[b:]
p.write_text(t, encoding="utf-8")

q = ROOT / "KH2-COOP-PLAN.md"
s = q.read_text(encoding="utf-8")
if "| 14 | Player 2's attack target |" not in s:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| 13 | What enemies drop")]
    assert len(idx) == 1
    lines.insert(idx[0] + 1, "| 14 | Player 2's attack target | **Each hero's attack motions test against his own lock-on target** "
                 "(a fault fix, 2026-11-11: the game used player 1's target for both, which is why the Grandstander ball "
                 "ignored player 2's hits). Player 2 now also does about twice the damage per swing window in the fight test. |")
    q.write_text("\n".join(lines), encoding="utf-8")
print("ok")
