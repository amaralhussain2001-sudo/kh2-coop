"""TEST ONLY: <base patch> + a RECORDER OF THE GAME'S OBJECT HEAP (register F4, eighth round). Never part of the
real patch. The same on both PCs.

Which heap: the freeze family "routine 0x00127A88 writes through address 0" asks the heap object in a1 for
count x 80 + 32 bytes (a pose table: 16 + 64 bytes a bone). Its callers (0x0017F9D8, 0x0017FA90, 0x0017FAB4) take
a1 from 0x001050C8 = the word at 0x0032BB1C: ONE heap object (class table 0x0033CC18: method 0 = allocate
0x001061D0, method 1 = free 0x001062B8), made at boot by 0x00105370.
Its layout (read in the program): +4 first byte, +8 end, +0xC bytes in use, +0x10 the newest block, +0x14 a first
block header. Every block: +0 next, +4 before, +8 size with header, +0xC the heap. Blocks lie in address order;
the free room after a block = next - (block + size).

What the kit records (block 0x000F1F80, read it with memdump_probe.py RANGES=000F1F80:40):
  +00 most bytes in use ever          +04 0x7FFFFFFF - the SMALLEST "largest free piece" ever seen
  +08 the game's counter then         +0C failed allocations (the heap returned 0)
  +10 size of the last failed one     +14 its caller (the address the caller passed in a2)
  +18 the biggest size ever asked     +1C its caller
  +20 in use now   +24 largest free piece now   +28 blocks now   +2C free bytes now (sum of the pieces)
  +30 most blocks ever                +34 0x7FFFFFFF - the smallest free sum ever
  +38 the heap's size (end - first byte)   +3C the heap object's address
The walk runs once a step from the player class's per-frame method (table word 0x0035241C, as make_godkit.py;
it chains to whatever is there, so it works on top of the HP kit and on a base with no patch).

  python -I tools/own/make_heapkit.py <baseDir> <outDir>
Memory: routines 0x000F1D00-0x000F1EFF, values 0x000F1F80-0x000F1FBF (the test recorders' block).
Hooks: 0x001061D0 (allocate, entry), 0x001062A4 (allocate, return), the table word.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1D00
V = 0x000F1F80
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
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
heap_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # the engine's player: once a step
    bne a0,t6,ht_old
    nop
    lui t7,0x0033
    lw t0,-17636(t7)              # the heap object (0x0032BB1C)
    beq t0,zero,ht_old
    nop
    lw t1,8(t0)                   # its end
    addiu t2,t0,20                # the first block header
    move t3,zero                  # largest free piece
    move t4,zero                  # free sum
    move t5,zero                  # blocks
ht_loop:
    lw t6,0(t2)                   # next
    lw t7,8(t2)                   # size
    sltu t8,t2,t6
    beq t8,zero,ht_end            # next must lie after this block (a broken list: stop)
    nop
    addu t7,t2,t7
    subu t7,t6,t7                 # free room after this block
    addu t4,t4,t7
    sltu t8,t3,t7
    movn t3,t7,t8
    addiu t5,t5,1
    sltiu t8,t5,30000
    beq t8,zero,ht_end
    nop
    bne t6,t1,ht_loop
    move t2,t6
ht_end:
    lui t9,%hi(V)
    addiu t9,t9,%lo(V)
    lw t7,12(t0)                  # bytes in use
    sw t7,0x20(t9)
    sw t3,0x24(t9)
    sw t5,0x28(t9)
    sw t4,0x2C(t9)
    sw t0,0x3C(t9)
    lw t6,4(t0)
    subu t6,t1,t6
    sw t6,0x38(t9)
    lw t6,0(t9)
    sltu t8,t6,t7
    beq t8,zero,ht_1
    nop
    sw t7,0(t9)
ht_1:
    lw t6,0x30(t9)
    sltu t8,t6,t5
    beq t8,zero,ht_2
    nop
    sw t5,0x30(t9)
ht_2:
    lui t6,0x7FFF
    ori t6,t6,0xFFFF
    subu t7,t6,t4                 # the free sum, turned round
    lw t8,0x34(t9)
    sltu t8,t8,t7
    beq t8,zero,ht_3
    nop
    sw t7,0x34(t9)
ht_3:
    subu t7,t6,t3                 # the largest free piece, turned round
    lw t8,4(t9)
    sltu t8,t8,t7
    beq t8,zero,ht_old
    nop
    sw t7,4(t9)
    lui t7,0x0035
    lw t6,-11076(t7)              # the game's counter 0x0034D4BC
    sw t6,8(t9)
ht_old:
    j @OLD@
    nop

ha_entry:                         # from 0x001061D0 (its first instruction ran in the delay slot: t7 = a1 + 15)
    lui t5,0x0033
    lw t5,-17636(t5)
    bne a0,t5,ha_back
    nop
    lui t5,%hi(V)
    addiu t5,t5,%lo(V)
    lw t6,0x18(t5)
    sltu t6,t6,a1
    beq t6,zero,ha_back
    nop
    sw a1,0x18(t5)
    sw a2,0x1C(t5)
ha_back:
    j 0x001061D8
    lw t5,16(a0)                  # the second instruction of the routine

ha_ret:                           # from 0x001062A4 (the routine's "jr ra")
    bne v0,zero,ha_r1
    nop
    lui t5,0x0033
    lw t5,-17636(t5)
    bne a0,t5,ha_r1
    nop
    lui t5,%hi(V)
    addiu t5,t5,%lo(V)
    lw t6,0x0C(t5)
    addiu t6,t6,1
    sw t6,0x0C(t5)
    sw a1,0x10(t5)
    sw a2,0x14(t5)
ha_r1:
    jr ra
    nop
""".replace("@OLD@", "0x%08X" % old)
code, labels = assemble(AT, SRC, {"V": V})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1F00, len(code)


def jmp(target):
    return 0x08000000 | ((target >> 2) & 0x03FFFFFF)


used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_heapkit.py): a recorder of the object heap, for tests only."]
words = [(AT + 4 * i, w) for i, w in enumerate(code)]
words += [(0x001061D0, jmp(labels["ha_entry"])), (0x001061D4, 0x24AF000F),      # j ha_entry / addiu t7,a1,15
          (0x001062A4, jmp(labels["ha_ret"]))]                                  # j ha_ret (the nop after it stays)
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["heap_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words; the old method %08X)" % (len(code), old))
