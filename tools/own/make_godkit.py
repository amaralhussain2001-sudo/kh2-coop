"""TEST ONLY: <base patch> + "both heroes keep their HP" (2026-11-13, for the long crash tests of the new job list:
Data Roxas, the 1000 Heartless, the bosses that carry a hero). The same on both PCs. Never part of the real patch.

How: the player class's per-frame method (class table 0x00352410, word +0x0C at 0x0035241C; the merged patch has
lane N's n_tick there) first goes through god_tick: when the object is player 1's hero (0x0034E948) or the twin
(0x000F05CC) and has a unit slot (object + 0x48C), the slot's most HP (+4) and HP (+0) are set to HP_VALUE.
A big hit of a late boss can still take more than HP_VALUE in one step; that is rare. Then the old method runs.
The game's own HP rules are untouched otherwise (a hero who is not hit simply stays full).

  python -I tools/own/make_godkit.py <baseDir> <outDir> [hp]      (hp default 150, the game's range at level 99)
Memory: 0x000F1C00-0x000F1CFF (the test recorders' block, as make_killkit.py: never both kits together).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
hp = int(sys.argv[3]) if len(sys.argv) > 3 else 150
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
if old is None:                     # a base with no patch at that word (a stock control): the game's own method
    old = 0x00178758
    at_line = len(text)
    text.append("")
SRC = """
god_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # player 1's hero
    beq a0,t6,gt_go
    nop
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne a0,t6,gt_old
    nop
gt_go:
    beq a0,zero,gt_old
    nop
    lw t6,0x48C(a0)               # his unit slot
    beq t6,zero,gt_old
    nop
    addiu t7,zero,@HP@
    sw t7,4(t6)
    sw t7,0(t6)
gt_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old).replace("@HP@", str(hp))
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_godkit.py hp %d): for tests only." % hp]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["god_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "hp", hp, "(%d words; the old method %08X)" % (len(code), old))
