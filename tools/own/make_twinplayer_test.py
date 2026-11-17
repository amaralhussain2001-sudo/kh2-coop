"""TEST ONLY: <own-screen patch> + "the engine's player pointer (0x0034E948) is the TWIN" (written before every
HUD run of the two-view mode). To see which special rules depend on that pointer (for example the Grandstander
ball). Camera and HUD follow the twin in such a run; never for play.
  python -I tools/own/make_twinplayer_test.py <baseDir> <outDir>
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F4980
OWN_HUD = 0x000F4000
SRC = """
t_swap:
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,ts_go
    lui t5,0x0035
    sw t6,-5816(t5)               # 0x0034E948: the engine's player
ts_go:
    j OWN_HUD
    nop
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {"OWN_HUD": OWN_HUD})
jal_old = "%08X" % ((3 << 26) | (OWN_HUD >> 2))
jal_new = "%08X" % ((3 << 26) | (labels["t_swap"] >> 2))
n = 0
for i, l in enumerate(text):
    if l.startswith("patch=1,EE,000F75") and l.endswith(",word," + jal_old):
        text[i] = l[:-8] + jal_new
        n += 1
assert n == 2, "expected the two calls of own_hud, found %d" % n
used = {l.split(",")[2] for l in text if l.startswith("patch=")}
add = ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
for l in add:
    assert l.split(",")[2] not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME)
