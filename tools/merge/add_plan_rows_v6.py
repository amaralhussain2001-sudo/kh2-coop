"""One-off: add the decisions of the night of 2026-11-10 to the decision table of KH2-COOP-PLAN.md."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 10 | Drive gauge |" in t:
    raise SystemExit("already there")
lines = t.split("\n")
idx = [i for i, l in enumerate(lines) if l.startswith("| 9 | Reaction Commands that carry the hero")]
assert len(idx) == 1
new = [
    "| 10 | Drive gauge | **Each hero has his own** (the user asked \"each person will have his own?\"; then said \"for your question use the Recommended\", 2026-11-10 night; the recommended option was own gauges). Each player's hits fill only his own; the values stay apart across rooms (merged build 6). Max bars and Drive levels stay common. The save file holds player 1's values. |",
    "| 11 | Munny, items, skills | **Munny and the item stock are common** (one wallet, as the game has it). Level, abilities and equipment are the same for both (row 2 and row 3). The user asked \"is the money shared, but their skills different?\" on 2026-11-10 night; answered: shared wallet, same skills today; own skills and equipment stay a Phase 4 job unless the user asks for it sooner. |",
    "| 12 | Text boxes | **Either player's Circle closes tutorial boxes and talk text** (taken as the recommended option 2026-11-10 night; before, only controller 1 could, and player 2 could open a dialogue but not close it). START, the main menu and the save menu are still controller 1 only. |",
    "| 13 | What enemies drop (HP, MP, Drive balls, munny) | **Both heroes pick them up.** HP / MP / Drive go to the hero who took the ball, munny into the one wallet. When both heroes stand in reach, every other ball asks player 2's hero first (taken as the recommended option 2026-11-10 night). |",
]
lines[idx[0] + 1:idx[0] + 1] = new
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: rows 10-13 added")
