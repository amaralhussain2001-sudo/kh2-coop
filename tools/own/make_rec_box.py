"""TEST ONLY (tenth round, glue 74 --boxpick): <base patch> + A COUNT OF ITEM BOXES. The same on both PCs. Never part of the real patch.
  0x000F1D00  boxes made (0x001BF620(item, place) was called)
  0x000F1D04  boxes taken by player 1's hero (0x001BF378(box, taker) with taker = the word at 0x0034E948)
  0x000F1D08  boxes taken by player 2's hero (taker = the twin, 0x000F05CC)
  0x000F1D0C  boxes taken by anybody else
  0x000F1D10  the item of the last box made (a0 of 0x001BF620)
Hooks: the first words of 0x001BF378 (addiu sp,sp,-80) and 0x001BF620 (addiu sp,sp,-48) jump here; the routines run on after the
count. Code 0x000F1F00 .. 0x000F1F7F (the recorders' block: not together with make_rec_cap3.py / make_rec_rc.py / make_rec_offer2.py).
Read the words with sweepm_probe.py (RANGES=000F1D00:14).
  python -I tools/own/make_rec_box.py <baseDir> <outDir>
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1F00
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
SRC = """
rb_take:                          # from 0x001BF378 (j): a0 = the box, a1 = the taker
    lui t7,0x000F
    lui t6,0x0035
    lw t6,-5816(t6)               # player 1's hero
    beq a1,t6,rbt_1
    addiu t5,zero,0x1D04
    lw t6,0x05CC(t7)              # player 2's hero
    beq a1,t6,rbt_1
    addiu t5,zero,0x1D08
    addiu t5,zero,0x1D0C
rbt_1:
    addu t5,t5,t7
    lw t4,0(t5)
    addiu t4,t4,1
    sw t4,0(t5)
    addiu sp,sp,-80               # the instruction that sat at 0x001BF378
    j 0x001BF37C
    nop
rb_make:                          # from 0x001BF620 (j): a0 = the item, a1 = the place
    lui t7,0x000F
    lw t4,0x1D00(t7)
    addiu t4,t4,1
    sw t4,0x1D00(t7)
    sw a0,0x1D10(t7)
    addiu sp,sp,-48               # the instruction that sat at 0x001BF620
    j 0x001BF624
    nop
"""
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1F80
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
for a in ("001BF378", "001BF620"):
    assert a not in used, a
add = ["comment=TEST RECORDER (tools/own/make_rec_box.py): item boxes made and taken by whom. For tests only."]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
add.append("patch=1,EE,001BF378,word,%08X" % ((2 << 26) | ((labels["rb_take"] >> 2) & 0x3FFFFFF)))
add.append("patch=1,EE,001BF620,word,%08X" % ((2 << 26) | ((labels["rb_make"] >> 2) & 0x3FFFFFF)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words at %08X)" % (len(code), AT))
