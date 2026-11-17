"""TEST ONLY (ninth round, the fault line "pc 0x00168B38, address 4" = register F8): <base patch> + a recorder at
the file pool's "finish" routine 0x0016FDA8(entry) that notes ONLY the calls for an entry of kind 1 (an effect
file) WITHOUT A PLACE (entry + 0x30 = 0): the call that makes the game read address 4.
  0x000F1D00  count of such calls
  0x000F1D10  the first 6 calls, 0x40 bytes each: return address, the entry, its number (+ 0x28), its word + 0x38,
              the game's counter, 3 spare words, then 0x20 bytes of the entry's name (+ 4)
  0x000F1E90  first call only: 0x160 bytes of the stack from sp
Read it with tools/own/recfin_probe.py. Never part of the real patch.
  python -I tools/own/make_rec_fin.py <baseDir> <outDir>
Memory 0x000F1C00-0x000F1FFF (the test recorders' block)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
HOOK = 0x0016FDA8
SRC = """
rec:
    lbu t6,0(a0)
    addiu t5,zero,1
    bne t6,t5,rec_out             # not an effect file
    lw t6,0x30(a0)
    bne t6,zero,rec_out           # it has a place
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    sltiu t4,t6,6
    beq t4,zero,rec_out
    sll t6,t6,6
    addu t6,t6,t7
    sw ra,0x1D10(t6)
    sw a0,0x1D14(t6)
    lw t4,0x28(a0)
    sw t4,0x1D18(t6)
    lw t4,0x38(a0)
    sw t4,0x1D1C(t6)
    lui t4,%hi(0x0034D4BC)
    lw t4,%lo(0x0034D4BC)(t4)
    sw t4,0x1D20(t6)
    addiu t4,zero,8
    addiu t3,a0,4
rec_n:
    lw t8,0(t3)
    sw t8,0x1D30(t6)
    addiu t3,t3,4
    addiu t4,t4,-1
    bgtz t4,rec_n
    addiu t6,t6,4
    addiu t4,zero,1
    bne t5,t4,rec_out
    addiu t6,t7,0x1E90
    move t5,sp
    addiu t4,sp,0x160
rec_l:
    lw t8,0(t5)
    sw t8,0(t6)
    addiu t5,t5,4
    bne t5,t4,rec_l
    addiu t6,t6,4
rec_out:
    addiu sp,sp,-80
    j 0x0016FDB0
    addiu t7,zero,1
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_fin.py): for tests only."]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,%08X,word,%08X" % (HOOK, (2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,%08X,word,00000000" % (HOOK + 4))
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
