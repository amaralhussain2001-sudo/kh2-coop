"""TEST ONLY (tenth round, glue 77 --gummiall): <base patch (a Gummi route kit, -gum0 ..)> + "the player ships' cannon blocks are
built as another weapon kind". The same on both PCs. Never part of the real patch.
READ (research of 2026-11-16, agentC): the flight module's weapon block builder 0x01F32460 reads the block's kind at 0x01F324D8
(lw t7,0(s4); s4 = the block record, s6 = the parent = ship + 0x3E0 for a player's ship, whose first word is the ship class table
0x01F81060). Kinds 493 .. 498 are the cannons (weapon types 64 .. 67); 499 / 500 / 501 = types 73 / 74 / 75 and 505 / 506 = 71 / 72
fire through the generic weapon class (0x01F49B38) with the same fire button (role 1). This kit makes 0x01F324D8 a "jal kk" while
the flight module is in memory (0x01F18014 = 0x636A); kk reads the kind as the game does and, for a cannon block of a PLAYER's ship
(not an enemy's, not a Teeny Ship's), gives the kit's kind instead. Memory 0x000F1C80-0x000F1CFF (not with make_lowkit.py /
make_lbkit.py).
  python -I tools/own/make_gumweapon.py <baseDir> <outDir> <kind>        (e.g. 499 or 505)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C80
base, out, kind = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
assert 300 <= kind <= 700
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
SRC = """
kk:                               # from 0x01F324D8 (jal; its delay slot addiu t6,zero,1 stays): the block's kind into t7
    lw t7,0(s4)                   # the instruction that sat there
    addiu t5,t7,-493
    sltiu t5,t5,6                 # a cannon block (493 .. 498)?
    beq t5,zero,kk_out
    lui t4,0x0010
    sltu t5,s6,t4
    bne t5,zero,kk_out            # no parent
    nop
    lw t5,-992(s6)                # the parent = ship + 0x3E0: the ship's class table?
    lui t4,0x01F8
    ori t4,t4,0x1060
    bne t5,t4,kk_out              # not a player's ship: as it is
    nop
    addiu t7,zero,@KIND@
kk_out:
    jr ra
    nop
""".replace("@KIND@", str(kind))
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_gumweapon.py %d): the player ships' cannon blocks are weapon kind %d. For tests only." % (kind, kind)]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
add.append("patch=1,EE,E001636A,extended,01F18014")
add.append("patch=1,EE,21F324D8,extended,%08X" % ((3 << 26) | ((labels["kk"] >> 2) & 0x3FFFFFF)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words at %08X; kind %d)" % (len(code), AT, kind))
