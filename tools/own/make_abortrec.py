"""TEST ONLY: a recorder at the C library's abort() (0x002FD160). The game leaves to the PS2 browser when abort()
runs (eighth round, fault F6: player 2 picks a second Drive Form -> black picture, memory wiped). This kit keeps
the game alive instead: it notes who called, copies the stack and then spins for ever, so a probe can read it.
  0x000E7100  count of calls (1 after the catch)
  0x000E7104  return address, 0x000E7108 sp, 0x000E710C a0, 0x000E7110 the game's counter 0x0034D4BC
  0x000E7120  0x400 bytes of the stack from sp (the callers' saved registers and return addresses)
Read it with tools/own/sweepm_probe.py RANGES=000E7100:20,000E7120:400 or tools/own/abort_probe.py.
Never part of the real patch.
  python -I tools/own/make_abortrec.py <baseDir> <outDir> [hexAddress ...]     (default: abort 002FD160 and exit 002FD348;
  the game's own "data error" exits are op_oef2_texture_load 0x0020E4C0 and op_oef2_clut_load 0x0020E570)
Memory 0x000E7000-0x000E751F (zero and unused by the patches up to merge_v7: its glues start at 0x000E8000).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000E7000
hooks = [int(x, 16) for x in sys.argv[3:]] or [0x002FD160, 0x002FD348]      # abort(), exit()
SRC = """
rec:
    lui t7,0x000E
    ori t7,t7,0x7100
    lw t6,0(t7)
    addiu t6,t6,1
    sw t6,0(t7)
    sw ra,4(t7)
    sw sp,8(t7)
    sw a0,12(t7)
    lui t4,0x0035
    lw t4,-11076(t4)              # the game's counter 0x0034D4BC
    sw t4,16(t7)
    addiu t6,t7,0x20
    move t5,sp
    addiu t4,sp,0x400
rec_l:
    lw t8,0(t5)
    sw t8,0(t6)
    addiu t5,t5,4
    bne t5,t4,rec_l
    addiu t6,t6,4
rec_spin:
    beq zero,zero,rec_spin
    nop
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000E7100, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_abortrec.py, routines %s): for tests only." % " ".join("%08X" % h for h in hooks)]
words = [(AT + 4 * k, w) for k, w in enumerate(code)]
for hook in hooks:
    words += [(hook, (2 << 26) | (labels["rec"] >> 2)), (hook + 4, 0)]
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
