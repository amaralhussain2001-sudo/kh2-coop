"""TEST ONLY (ninth round, the pickup test of 2026-11-15 night): <base patch WITH the god kit (make_godkit.py)> + "MP 10, Drive 0 for
both heroes, once": for 30 steps from session frame <frame> (game counter = frame - 152), each hero's unit slot gets MP 10
(slot + 0x180), Drive gauge 0 and Drive bars 0 (slot + 0x1B0 / + 0x1B1). So MP and Drive balls show who took them. low_tick takes
the player class's per-frame word (0x0035241C, the god kit's god_tick) and then runs it. Memory 0x000F1C80-0x000F1CFF (the god
kit's block: god_tick sits at 0x000F1C00 .. 0x000F1C44). Never part of the real patch.
  python -I tools/own/make_lowkit.py <baseDir> <outDir> <sessionFrame>"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C80
TABLE_WORD = 0x0035241C
base, out, frame = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old, at_line = None, None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old, at_line = int(m.group(1), 16), i
assert old == 0x000F1C00, "the base must carry the god kit (god_tick at 0x000F1C00): %s" % old
SRC = """
low_tick:
    lui t7,0x0035
    lw t5,-11076(t7)              # the game's counter
    addiu t5,t5,-%d
    sltiu t5,t5,30
    beq t5,zero,lt_old
    lw t6,-5816(t7)               # player 1's hero (the engine's player)
    beq a0,t6,lt_go
    nop
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne a0,t6,lt_old
    nop
lt_go:
    beq a0,zero,lt_old
    nop
    lw t6,0x48C(a0)               # his unit slot
    beq t6,zero,lt_old
    addiu t7,zero,10
    sw t7,0x180(t6)               # MP 10
    sb zero,0x1B0(t6)             # Drive gauge 0
    sb zero,0x1B1(t6)             # Drive bars 0
lt_old:
    j 0x000F1C00
    nop
""" % (frame - 152)
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F1D00, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_lowkit.py %d): MP 10, Drive 0 for both heroes once. For tests only." % frame]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["low_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
