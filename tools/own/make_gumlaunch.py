"""TEST ONLY: <base patch> + lane S3's launcher as a kit: when the world map's cursor ship is built (the call at
0x002C5F08), the game's own "start Gummi route N" (0x002C5418) is called once. Then the base patch's call (the
twenty-fourth glue's pad_both, or the game's controller getter) runs. Routine at 0x000F1C00 (the test block), latch
0x000F1CF0. Same on both PCs. Never part of the real patch.
  python -I tools/own/make_gumlaunch.py <baseDir> <outDir> [route 0..8]"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
SITE = 0x002C5F08
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
route = int(sys.argv[3]) if len(sys.argv) > 3 else 0
text = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
old, at_line = 0x00167F18, None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % SITE, l)
    if m:
        old, at_line = (int(m.group(1), 16) & 0x03FFFFFF) << 2, i
SRC = """
gl:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000F
    lw t6,0x1CF0(t7)
    bne t6,zero,gl_pad
    li t6,1
    sw t6,0x1CF0(t7)
    jal 0x002C5418
    li a0,%d
gl_pad:
    ld ra,0(sp)
    move a0,zero
    j 0x%08X
    addiu sp,sp,16
""" % (route, old)
code, labels = assemble(0x000F1C00, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
add = ["comment=TEST KIT (tools/own/make_gumlaunch.py route %d): for tests only." % route]
add += ["patch=1,EE,%08X,word,%08X" % (0x000F1C00 + 4 * i, w) for i, w in enumerate(code)]
line = "patch=1,EE,%08X,word,%08X" % (SITE, (3 << 26) | (0x000F1C00 >> 2))
if at_line is None:
    add.append(line)
else:
    text[at_line] = line
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "route", route, "(then %08X)" % old)
