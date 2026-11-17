"""TEST ONLY: <base patch> + a recorder at "a control object opens the board menu" (0x001BDBD4 in 0x001BDB70):
ring of 8 pairs (control object, return address of 0x001BDB70's caller) at 0x000F5F08, write index at 0x000F5F00.
  python -I tools/own/make_dbg_board.py <baseDir> <outDir>
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
SRC = """
dbg:
    lui t7,0x000F
    lw t6,0x5F00(t7)
    andi t6,t6,0x38
    addu t5,t7,t6
    sw s0,0x5F08(t5)
    ld t4,48(sp)
    ld t4,104(sp)
    sw t4,0x5F0C(t5)
    sw s2,0x5F08(t5)
    addiu t6,t6,8
    sw t6,0x5F00(t7)
    jr ra
    daddu a0,s0,zero
"""
code, labels = assemble(0x000F5E00, SRC, {})
text = (ROOT / sys.argv[1] / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
text += ["patch=1,EE,%08X,word,%08X" % (0x000F5E00 + 4 * i, w) for i, w in enumerate(code)]
text.append("patch=1,EE,001BDBD4,word,%08X" % ((3 << 26) | (labels["dbg"] >> 2)))
out = ROOT / sys.argv[2]
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text) + "\n", encoding="utf-8")
print(out)
