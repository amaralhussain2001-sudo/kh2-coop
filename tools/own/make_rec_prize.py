"""TEST ONLY (ninth round, after the user's question on pickups, 2026-11-15 night): <base patch> + a recorder at the entry of the
game's "a prize takes effect" routine 0x001A52A8 (a1 = the character who took it, a2 = the prize's data, byte + 0x14 = its kind,
an index into the table at 0x0036D578: HP / MP / munny / Drive / ...). It counts, for each kind 0 .. 31, how many prizes went to
player 1's hero (row 0), to player 2's hero (row 1) and to anybody else (row 2: Donald, Goofy, a guest).
  0x000F1D10 + 4 x (32 x row + kind)  the counts (3 rows, 0x180 bytes)
Code at 0x000F1EA0 (the block 0x000F1D00-0x000F1FFF: never with make_rec_cap3.py, make_rec_rc.py or make_rec_offer2.py).
The routine's first two instructions (addiu sp,sp,-32 / mtc1 zero,f0) are made in the recorder, then it jumps to 0x001A52B0.
Never part of the real patch.
  python -I tools/own/make_rec_prize.py <baseDir> <outDir>"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1EA0
HOOK = 0x001A52A8
SRC = """
rec:
    lui t7,0x000F
    lbu t6,20(a2)
    andi t6,t6,31
    lui t5,0x0035
    lw t5,0x2400(t5)
    beq a1,t5,r_p1
    lw t4,0x05CC(t7)
    beq a1,t4,r_p2
    addiu t3,zero,256
    b r_add
    nop
r_p1:
    b r_add
    addiu t3,zero,0
r_p2:
    addiu t3,zero,128
r_add:
    sll t6,t6,2
    addu t6,t6,t3
    addu t6,t6,t7
    lw t5,0x1D10(t6)
    addiu t5,t5,1
    sw t5,0x1D10(t6)
    addiu sp,sp,-32
    j 0x001A52B0
    mtc1 zero,f0
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F2000, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_prize.py): who takes which prize. For tests only."]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, x) for i, x in enumerate(code)]
add.append("patch=1,EE,%08X,word,%08X" % (HOOK, (2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,%08X,word,00000000" % (HOOK + 4))
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
