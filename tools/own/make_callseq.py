"""TEST ONLY: <base patch> + SEVERAL CALLS of routines of the game at one moment, one after the other, each with up
to three arguments (ninth round, plan row 39: "the game gives a thing" = 0x001A3188(item, character or 100, 0)
without playing to a chest). The same on both PCs. Never part of the real patch. make_callonce.py with a list.

  python -I tools/own/make_callseq.py <baseDir> <outDir> <sessionFrame> ROUTINE:A0:A1:A2 [ROUTINE:A0:A1:A2 ...]   (hex)
Memory: 0x000F1C00-0x000F1CEF, the "done" word 0x000F1CF0 (the test recorders' block: never together with the
other kits that use it).
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
frame = int(sys.argv[3])
calls = [[int(x, 16) for x in c.split(":")] + [0, 0, 0] for c in sys.argv[4:]]
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
    if v < 0x8000:
        return "    addiu %s,zero,%d\n" % (reg, v)
    return "    lui %s,0x%04X\n    ori %s,%s,0x%04X\n" % (reg, v >> 16, reg, reg, v & 0xFFFF)


body = ""
for c in calls:
    body += load("a0", c[1]) + load("a1", c[2]) + "    jal 0x%08X\n" % c[0] + load("a2", c[3]).split("\n")[0] + "\n"
    assert c[3] < 0x8000, "the third argument must fit into one instruction (it sits in the delay slot)"
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
@BODY@    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
co_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old).replace("@N@", str(count)).replace("@BODY@", body)
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1CF0, "%d words do not fit" % len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_callseq.py %s): for tests only." % " ".join(sys.argv[3:])]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["co_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "%d calls at session frame %d (%d words; the old method %08X)" % (len(calls), frame, len(code), old))
