"""TEST ONLY: <base patch> + "the script engine's button tests see BOTH controllers".
The two built-ins of the script engine's table (0x0034DB30 -> 0x0016DB98 "button held", 0x0034DB38 -> 0x0016DBE0
"button pressed") read logical controller 0 through the getter 0x00167F18. Here they get a scratch record with
the held / pressed words of controller 0 OR controller 1.
  python -I tools/merge/make_padboth_test.py <baseDir> <outDir>
"""
import pathlib
import sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F4740
SRC = """
pad_both:
    lui t7,0x0035
    addiu t6,t7,-10560            # 0x0034D6C0: logical controller 0 (controller 1 is 0x60 further)
    ld t5,0(t6)
    ld t4,0x60(t6)
    or t5,t5,t4
    lui v0,0x000F
    addiu v0,v0,0x47E0            # scratch record
    sd t5,0(v0)
    ld t5,8(t6)
    ld t4,0x68(t6)
    or t5,t5,t4
    jr ra
    sd t5,8(v0)
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
jal = (3 << 26) | ((labels["pad_both"] >> 2) & 0x3FFFFFF)
used = {l.split(",")[2] for l in text if l.startswith("patch=")}
add = ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add += ["patch=1,EE,0016DBA8,word,%08X" % jal, "patch=1,EE,0016DBF0,word,%08X" % jal]
for l in add:
    assert l.split(",")[2] not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(add), "words added")
