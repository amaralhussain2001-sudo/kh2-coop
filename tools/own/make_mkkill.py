"""TEST ONLY: <base patch> + "King Mickey loses all his HP at a given frame" (eighth round, plan row 45: what does
the game do when the King falls while TWO Mickeys play). The kill kit (make_killkit.py) sits in the hero class's
per-frame method and never sees a Mickey; this one sits in King Mickey's own (class table 0x00352360, word + 0x0C
at 0x0035236C, the game's method 0x001D03A0): at the given game counter the object's HP-change method (class
+ 0x78) is called with -9999, once, for the first Mickey that is updated in that step. The same on both PCs.
  python -I tools/own/make_mkkill.py <baseDir> <outDir> <sessionFrame>
Memory 0x000E7600-0x000E76FF (zero and unused by the patches). Never part of the real patch.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000E7600
TABLE_WORD = 0x0035236C
OLD = 0x001D03A0
base, out, frame = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
SRC = """
mk_tick:
    lui t7,0x0035
    lw t2,-11076(t7)              # the game's frame counter 0x0034D4BC
    li t0,%d
    subu t2,t2,t0
    sltiu t2,t2,2
    beq t2,zero,mk_old
    lui t6,0x000E
    lw t5,0x76F0(t6)
    bne t5,zero,mk_old            # done once
    li t5,1
    sw t5,0x76F0(t6)
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    lw t7,0(a0)
    lw t7,0x78(t7)
    li a1,-9999
    move a2,zero
    jalr t7                       # his HP change: all of it
    move a3,zero
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
mk_old:
    j 0x%08X
    nop
""" % ((frame - 152) & 0x7FFF, OLD)
assert frame - 152 < 0x8000
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000E76F0, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_mkkill.py, King Mickey falls at frame %d): for tests only." % frame]
for a, w in [(AT + 4 * k, w) for k, w in enumerate(code)] + [(TABLE_WORD, labels["mk_tick"])]:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
