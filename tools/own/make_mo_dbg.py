"""TEST ONLY (part 141): <patch dir> -> <out dir> with a recorder in front of the seventy-ninth glue's po_pad: every call of pad_both
(0x000F4740) that is NOT the field's START look-out (return 0x00138540) nor the command menu's first button (0x0013C7A0) writes its
return address to 0x000DE80C and the game's counter to 0x000DE810 (read them with tools/own/mo_probe.py). The routine sits at
0x000DE400 (the glue's room ends at 0x000DE200; 0x000DE400 .. 0x000DE7FF holds no patch word).
  python -I tools/own/make_mo_dbg.py <patchDir> <outDir>"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

src_dir, out_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
NAME = "SLPM-66675_F266B00B.pnach"
text = (src_dir / NAME).read_text(encoding="utf-8")
words = {int(a, 16) & 0x0FFFFFFF: int(v, 16) for a, v in re.findall(r"patch=1,EE,([0-9A-F]{8}),word,([0-9A-F]{8})", text)}
first = words[0x000F4740]
assert first >> 26 == 2, "pad_both does not start with j po_pad"
po_pad = (first & 0x3FFFFFF) << 2
assert not [a for a in words if 0x000DE400 <= a < 0x000DE800]
SRC = """
dbg:
    lui t7,0x0013
    ori t7,t7,0x8540
    beq ra,t7,dbg_go
    lui t7,0x0013
    ori t7,t7,0xC7A0
    beq ra,t7,dbg_go
    lui t7,0x000E
    sw ra,-6132(t7)
    lui t6,0x0035
    lw t6,-11076(t6)
    sw t6,-6128(t7)
dbg_go:
    j PO_PAD
    nop
"""
code, _labels = assemble(0x000DE400, SRC, {"PO_PAD": po_pad})
code = [w if isinstance(w, int) else w[1] for w in code]
lines = [l for l in text.splitlines() if not l.startswith("patch=1,EE,000F4740,")]
lines.append("comment=TEST ONLY (tools/own/make_mo_dbg.py): pad_both's callers are recorded at 0x000DE80C / 0x000DE810.")
for i, w in enumerate(code):
    lines.append("patch=1,EE,%08X,word,%08X" % (0x000DE400 + 4 * i, w))
lines.append("patch=1,EE,000F4740,word,%08X" % ((2 << 26) | (0x000DE400 >> 2)))
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", out_dir / NAME, len(code), "words")
