"""TEST ONLY: <base patch> + "a hero loses all his HP at a given frame" (lane N's forced fall, as a kit for the
merged patches). The same on both PCs. Never part of the real patch.

How: the player class's per-frame method (class table 0x00352410, word +0x0C at 0x0035241C; the merged patch
has lane N's n_tick there) first goes through kill_tick: once a step, for the engine's player, a table of
(game counter, who) is looked at; when the counter 0x0034D4BC reaches an entry, that hero's own HP-change
method (class +0x78) is called with -9999. So the fall is the game's own (down, rescue, Game Over when both
are down). Then the old method runs.

  python -I tools/own/make_killkit.py <baseDir> <outDir> who@sessionFrame[,who@sessionFrame...]
  who = hero (player 1's) | twin.   Example: hero@7300,twin@7300 = a Game Over at frame 7300.
Memory: 0x000F1C00-0x000F1CFF (the test recorders' block; do not use together with a recorder kit).
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
ents = []
for part in sys.argv[3].split(","):
    who, frame = part.split("@")
    ents.append(((int(frame) - 152) & 0xFFFFFFFF, {"hero": 0, "twin": 1}[who]))
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
if old is None:                     # a base with no patch at that word (a stock control): the game's own method
    old = 0x00178758
    at_line = len(text)
    text.append("")
SRC = """
kill_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # the engine's player: once a step
    bne a0,t6,kt_old
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd s0,16(sp)
    lui s0,%hi(kt_table)
    addiu s0,s0,%lo(kt_table)
kt_loop:
    lw t0,0(s0)                   # the counter value of this entry (0 = the end)
    beq t0,zero,kt_done
    nop
    lui t7,0x0035
    lw t2,-11076(t7)              # the game's frame counter 0x0034D4BC
    subu t2,t2,t0
    sltiu t2,t2,2
    beq t2,zero,kt_next
    nop
    lw t4,4(s0)
    lui t7,0x0035
    lw a0,-5816(t7)               # 0 = player 1's hero
    beq t4,zero,kt_go
    nop
    lui t7,0x000F
    lw a0,0x05CC(t7)              # 1 = the twin
kt_go:
    beq a0,zero,kt_next
    nop
    lw t7,0x7F8(a0)
    andi t7,t7,4
    bne t7,zero,kt_next           # already down
    nop
    lw t7,0(a0)
    lw t7,0x78(t7)                # his own HP-change method
    addiu a1,zero,-9999
    move a2,zero
    jalr t7
    move a3,zero
kt_next:
    b kt_loop
    addiu s0,s0,8
kt_done:
    ld ra,0(sp)
    ld a0,8(sp)
    ld s0,16(sp)
    addiu sp,sp,32
kt_old:
    j @OLD@
    nop
kt_table:
""".replace("@OLD@", "0x%08X" % old)
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
for c, w in ents:
    code += [c, w]
code.append(0)
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_killkit.py %s): for tests only." % sys.argv[3]]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["kill_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, sys.argv[3], "(%d words; the old method %08X)" % (len(code), old))
