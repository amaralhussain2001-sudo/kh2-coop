"""TEST ONLY (ninth round, Gummi route 8): <base patch> + A LOOP THAT COSTS TIME IN EVERY FRAME OF A GUMMI FLIGHT, to see
whether the flight depends on how long a frame's work takes. The controller task's call at 0x00167E84 (the patch
has a jal to the twenty-sixth glue's gm_pre there) first goes through a loop of <count> rounds (3 instructions
each) while the flight module is in memory (0x636A at 0x01F18014), then on to the old target. Nothing else changes.
The same on both PCs. Never part of the real patch.
  python -I tools/own/make_burnkit.py <basePatchDir> <outDir> <count>
Memory: 0x000F1D40 .. 0x000F1D6F (the test recorders' block: not together with the capture log)."""
import pathlib
import re
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out, count = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
old = None
for l in lines:
    m = re.match(r"patch=1,EE,00167E84,word,([0-9A-Fa-f]{8})", l)
    if m:
        old = int(m.group(1), 16)
assert old is not None and (old >> 26) == 3, "the base patch has no jal at 0x00167E84"
target = (old & 0x03FFFFFF) << 2
AT = 0x000F1D40                                 # (0x000F1C00 is the Gummi launch kit's own routine: run g8-...-b2k crashed there)
code = [
    0x3C1801F2,                               # lui t8,0x01F2
    0x97188014,                               # lhu t8,-32748(t8)        0x01F18014: which module
    0x340F636A,                               # ori t7,zero,0x636A       the flight
    0x170F0006,                               # bne t8,t7,skip
    0x3C190000 | (count >> 16),               # lui t9,hi
    0x37390000 | (count & 0xFFFF),            # ori t9,t9,lo
    0x2739FFFF,                               # loop: addiu t9,t9,-1
    0x1720FFFE,                               # bne t9,zero,loop
    0x00000000,
    0x00000000,
    0x08000000 | (target >> 2),               # skip: j the old target
    0x00000000,
]
lines.append("comment=TEST KIT (tools/own/make_burnkit.py %d): a loop of %d rounds in every frame of a Gummi flight. For tests only." % (count, count))
for i, w in enumerate(code):
    lines.append("patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w))
lines.append("patch=1,EE,00167E84,word,%08X" % (0x0C000000 | (AT >> 2)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "| a loop of", count, "rounds; the old target %08X" % target)
