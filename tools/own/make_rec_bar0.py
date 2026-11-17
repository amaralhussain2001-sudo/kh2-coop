"""TEST ONLY (ninth round, the fault line "pc 0x00168B38, address 4" = register F8): <base patch> + a recorder at
0x00168B38(file, type, index) ("find a part of a packed file") that notes ONLY THE CALLS WITH FILE = 0.
  0x000F1D00  count of such calls
  0x000F1D10  the first 8 calls, 16 bytes each: return address, a1, a2, the game's counter
  0x000F1E10  first call only: 0x1C0 bytes of the stack from sp
Read it with tools/own/rec_probe.py (the same layout as make_rec_at.py). Never part of the real patch.
  python -I tools/own/make_rec_bar0.py <baseDir> <outDir>
Memory 0x000F1C00-0x000F1FFF (the test recorders' block)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
HOOK = 0x00168B38                 # lw t5,4(a0) / blez t5,0x00168B7C / (delay slot) daddu t6,zero,zero
SRC = """
rec:
    bne a0,zero,rec_go
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    andi t6,t6,15
    sll t6,t6,4
    addu t6,t6,t7
    sw ra,0x1D10(t6)
    sw a1,0x1D14(t6)
    sw a2,0x1D18(t6)
    lui t4,%hi(0x0034D4BC)
    lw t4,%lo(0x0034D4BC)(t4)
    sw t4,0x1D1C(t6)
    addiu t4,zero,1
    bne t5,t4,rec_go
    addiu t6,t7,0x1E10
    move t5,sp
    addiu t4,sp,0x1C0
rec_l:
    lw t8,0(t5)
    sw t8,0(t6)
    addiu t5,t5,4
    bne t5,t4,rec_l
    addiu t6,t6,4
rec_go:
    lw t5,4(a0)
    blez t5,rec_z
    move t6,zero
    j 0x00168B44
    nop
rec_z:
    j 0x00168B7C
    nop
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_bar0.py): for tests only."]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,%08X,word,%08X" % (HOOK, (2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,%08X,word,00000000" % (HOOK + 4))
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
