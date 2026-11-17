"""TEST ONLY: <base patch> + a recorder for the null result in the script built-in 0x0016E378 (fault at 0x0016E3C0).
Hook 0x0016E3A8 (jal 0x001DC5F8). On a null result: counter at 0x000F4A00, the object at 0x000F4A04, 24 words of
it from 0x000F4A10, 24 words of the record at object+8 from 0x000F4A70.
  python -I tools/own/make_diag_null.py <baseDir> <outDir>
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F4900
SRC = """
diag:
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x001DC5F8
    nop
    bne v0,zero,dg_out
    ld a0,8(sp)
    lui t7,0x000F
    lw t6,0x4A00(t7)
    addiu t6,t6,1
    sw t6,0x4A00(t7)
    sw a0,0x4A04(t7)
    addiu t5,t7,0x4A10
    addiu t4,a0,0x60
    move t3,a0
dg_a:
    lw t2,0(t3)
    sw t2,0(t5)
    addiu t3,t3,4
    bne t3,t4,dg_a
    addiu t5,t5,4
    lw t3,8(a0)
    beq t3,zero,dg_out
    addiu t4,t3,0x60
dg_b:
    lw t2,0(t3)
    sw t2,0(t5)
    addiu t3,t3,4
    bne t3,t4,dg_b
    addiu t5,t5,4
dg_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
used = {l.split(",")[2] for l in text if l.startswith("patch=")}
add = ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,0016E3A8,word,%08X" % ((3 << 26) | (labels["diag"] >> 2)))
for l in add:
    assert l.split(",")[2] not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME)
