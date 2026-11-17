"""TEST ONLY: <base patch> + THE GAME GIVES THINGS: from session frame <frame> on, once, the game's own "give" routine
0x001A3188(item, 100 = the bag, 0) is called for each item of a list (as a chest calls it: 0x001A83B4), from the
field's step (the patch's head of the calls at 0x00138538 is chained). The same on both PCs. Never part of the real patch.
  python -I tools/own/make_givekit.py <basePatchDir> <outDir> <frame> <itemHex>[*count] [...]
Memory: 0x000F1E40 .. 0x000F1EFF (the test recorders' block: not together with the capture log); done flag 0x000F1E3C."""
import pathlib
import re
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out, frame = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
items = []
for a in sys.argv[4:]:
    iid, _, n = a.partition("*")
    items += [int(iid, 16)] * (int(n) if n else 1)
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
old = None
for l in lines:
    m = re.match(r"patch=1,EE,00138538,word,([0-9A-Fa-f]{8})", l)
    if m:
        old = int(m.group(1), 16)
assert old is not None and (old >> 26) == 3, "the base patch has no jal at 0x00138538"
target = (old & 0x03FFFFFF) << 2
AT = 0x000F1E40
count = (frame - 152) & 0xFFFF
code = [
    0x3C0F0035,                               # 0  lui t7,0x0035
    0x8DEED4BC,                               # 1  lw t6,-11076(t7)      the game's counter
    0x340D0000 | count,                       # 2  ori t5,zero,frame - 152
    0x01CD702A,                               # 3  slt t6,t6,t5
    0x15C00000,                               # 4  bne t6,zero,go
    0x3C0C000F,                               # 5  lui t4,0x000F
    0x8D8B1E3C,                               # 6  lw t3,0x1E3C(t4)       done?
    0x15600000,                               # 7  bne t3,zero,go
    0x240B0001,                               # 8  addiu t3,zero,1
    0xAD8B1E3C,                               # 9  sw t3,0x1E3C(t4)
    0x27BDFFE0,                               # 10 addiu sp,sp,-32
    0xFFBF0000,                               # 11 sd ra,0(sp)
    0xFFB00008,                               # 12 sd s0,8(sp)
    0x3C10000F,                               # 13 lui s0,0x000F
    0x36100000,                               # 14 ori s0,s0,<the list>
    0x96040000,                               # 15 loop: lhu a0,0(s0)
    0x10800000,                               # 16 beq a0,zero,done
    0x24050064,                               # 17 addiu a1,zero,100   (the bag)
    0x0C000000 | (0x001A3188 >> 2),           # 18 jal 0x001A3188
    0x0000302D,                               # 19 daddu a2,zero,zero
    0x10000000,                               # 20 b loop
    0x26100002,                               # 21 addiu s0,s0,2
    0xDFBF0000,                               # 22 done: ld ra,0(sp)
    0xDFB00008,                               # 23 ld s0,8(sp)
    0x27BD0020,                               # 24 addiu sp,sp,32
    0x08000000 | (target >> 2),               # 25 go: j the old target
    0x00000000,                               # 26
]
LIST = AT + 4 * len(code)
code[14] |= LIST & 0xFFFF
code[4] |= (25 - 5) & 0xFFFF
code[7] |= (25 - 8) & 0xFFFF
code[16] |= (22 - 17) & 0xFFFF
code[20] |= (15 - 21) & 0xFFFF
half = items + [0]
if len(half) % 2:
    half.append(0)
code += [half[i] | (half[i + 1] << 16) for i in range(0, len(half), 2)]
assert AT + 4 * len(code) <= 0x000F1F00, "too many items"
lines.append("comment=TEST KIT (tools/own/make_givekit.py %s): the game gives these things once; for tests only." % " ".join(sys.argv[3:]))
for i, w in enumerate(code):
    lines.append("patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w))
lines = [l for l in lines if not l.startswith("patch=1,EE,00138538,word,")]
lines.append("patch=1,EE,00138538,word,%08X" % (0x0C000000 | (AT >> 2)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "| %d gives at frame %d; the old head %08X" % (len(items), frame, target))
