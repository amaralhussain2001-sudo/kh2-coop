"""TEST ONLY: <base patch> + ONE CALL of a routine of the game at one moment, with up to three arguments
(eighth round, plan row 39: "give the hero an ability" = 0x00188B68(record, number, on) without playing to a
level-up). The same on both PCs. Never part of the real patch.

How: the player class's per-frame method (class table 0x00352410, word + 0x0C at 0x0035241C; the merged patch has
a routine there already) first goes through co_tick: the first time player 1's hero is stepped with the game's
frame counter (0x0034D4BC = session frame - 152) at or past the given frame, the routine is called once.

  python -I tools/own/make_callonce.py <baseDir> <outDir> <sessionFrame> <hexRoutine> [hexA0 [hexA1 [hexA2]]]
Memory: 0x000F1C00-0x000F1CEF, the "done" word 0x000F1CF0 (the test recorders' block: never together with the
other kits that use it, such as make_godkit.py or the recorders).
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
frame, fn = int(sys.argv[3]), int(sys.argv[4], 16)
args = [int(x, 16) for x in sys.argv[5:8]] + [0, 0, 0]
count = frame - 152
assert 0 < count < 0x8000
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
assert old is not None, "the base has no routine at the player class's per-frame word"


def load(reg, v):
    return "    lui %s,0x%04X\n    ori %s,%s,0x%04X\n" % (reg, v >> 16, reg, reg, v & 0xFFFF)


SRC = """
co_tick:
    lui t7,0x000F
    lw t6,0x1CF0(t7)              # done already
    bne t6,zero,co_old
    lui t5,0x0035
    lw t4,-11076(t5)              # 0x0034D4BC: the game's frame counter
    addiu t3,zero,@N@
    slt t3,t4,t3
    bne t3,zero,co_old            # not yet
    nop
    lw t3,-5816(t5)               # only in the step of player 1's hero
    bne a0,t3,co_old
    addiu t3,zero,1
    sw t3,0x1CF0(t7)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
@A0@@A1@@A2@    jal @FN@
    nop
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
co_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old).replace("@N@", str(count)).replace("@FN@", "0x%08X" % fn)
SRC = SRC.replace("@A0@", load("a0", args[0])).replace("@A1@", load("a1", args[1])).replace("@A2@", load("a2", args[2]))
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1CF0
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_callonce.py %s): for tests only." % " ".join(sys.argv[3:])]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["co_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "one call of %08X(%08X, %08X, %08X) at session frame %d (%d words; the old method %08X)" % (fn, args[0], args[1], args[2], frame, len(code), old))
