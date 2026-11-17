"""Static survey of the boss scripts (seventh round, job 7): which of the decoded boss AI scripts
(local/analysis/h/ai/B_*.txt, lane H's decoder) ask the engine for "the player" (trap_sysobj_player), which
attach, hook or capture an object (trap names with hook / attach / capture / is_ride) and which read a controller
(trap_pad_*). Writes local/analysis/boss-survey.txt and prints the totals.
  python -I tools/own/boss_survey.py"""
import collections
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
AI = ROOT / "local" / "analysis" / "h" / "ai"
HOLD = re.compile(r"trap_\w*(hook|attach|capture|is_ride)\w*")
rows, names = [], collections.Counter()
tot = collections.Counter()
for f in sorted(AI.glob("B_*.txt")):
    text = f.read_text(encoding="utf-8", errors="replace")
    traps = collections.Counter(re.findall(r"trap_[a-z_0-9]+", text))
    player = traps.get("trap_sysobj_player", 0)
    hold = {k: v for k, v in traps.items() if HOLD.fullmatch(k)}
    pad = {k: v for k, v in traps.items() if k.startswith("trap_pad_")}
    for k in list(hold) + list(pad):
        names[k] += 1
    tot["scripts"] += 1
    tot["ask for the player"] += 1 if player else 0
    tot["calls of trap_sysobj_player"] += player
    tot["hold / hook an object"] += 1 if hold else 0
    tot["read a controller"] += 1 if pad else 0
    tot["hold or read a controller"] += 1 if (hold or pad) else 0
    rows.append("%-26s player %2d  hold %-40s pad %s" % (f.stem, player, ",".join(sorted(hold)) or "-", ",".join(sorted(pad)) or "-"))
out = ["%s: %d" % kv for kv in tot.items()] + ["", "trap names counted as hold / pad (scripts using them):"]
out += ["  %-34s %d" % kv for kv in sorted(names.items())] + [""] + rows
(ROOT / "local" / "analysis" / "boss-survey.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out[:8 + len(names)]))
