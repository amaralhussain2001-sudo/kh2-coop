"""TEST ONLY: bit-coded search for the place that decides "only the engine's player may do this".
Every load of the engine's player pointer (lw reg,-5816(base) with base = 0x00350000, 0x0034E948) gets an index.
Variant b: the loads whose index has bit b set read 0x0034E954 instead (a word the program never addresses), and a
small routine in front of the two-view HUD runs keeps that word = the TWIN (or the player when there is no twin).
So in variant b those places see the twin as "the player".
  python -I tools/own/make_playerbits.py <baseDir> <outPrefix> [lo hi]     (only sites with lo <= address < hi)
  python -I tools/own/make_playerbits.py <baseDir> <outDir> only <idx,idx,...>
"""
import pathlib
import struct
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402
import mips  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F4980
OWN_HUD = 0x000F4000
SRC = """
t_mirror:
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    lui t5,0x0035
    bne t6,zero,tm_set
    nop
    lw t6,-5816(t5)               # no twin: the engine's player
tm_set:
    sw t6,-5804(t5)               # 0x0034E954: test word "the other player"
    j OWN_HUD
    nop
"""
base = ROOT / sys.argv[1]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
used = {int(l.split(",")[2], 16) for l in text if l.startswith("patch=")}
e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
lo, hi = 0x00100000, 0x00400000
only = None
if len(sys.argv) > 4 and sys.argv[3] == "only":
    only = {int(x) for x in sys.argv[4].split(",")}
elif len(sys.argv) > 4:
    lo, hi = int(sys.argv[3], 16), int(sys.argv[4], 16)
sites = []
for i, w in enumerate(words):
    if (w >> 26) != 0x23 or (w & 0xFFFF) != 0xE948:
        continue
    b = (w >> 21) & 31
    ok = False
    for j in range(i - 1, max(i - 25, -1), -1):
        x = words[j]
        if (x >> 26) == 0x0F and ((x >> 16) & 31) == b:
            ok = (x & 0xFFFF) == 0x0035
            break
    pc = va + 4 * i
    if ok and pc not in used and lo <= pc < hi:
        sites.append((pc, w))
print("sites:", len(sites))
code, labels = assemble(AT, SRC, {"OWN_HUD": OWN_HUD})
jal_old = "%08X" % ((3 << 26) | (OWN_HUD >> 2))
jal_new = "%08X" % ((3 << 26) | (labels["t_mirror"] >> 2))
common = list(text)
n = 0
for i, l in enumerate(common):
    if l.startswith("patch=1,EE,000F75") and l.endswith(",word," + jal_old):
        common[i] = l[:-8] + jal_new
        n += 1
assert n == 2
common += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]


def write(out, chosen):
    out.mkdir(parents=True, exist_ok=True)
    add = ["patch=1,EE,%08X,word,%08X" % (pc, (w & 0xFFFF0000) | 0xE954) for pc, w in chosen]
    (out / NAME).write_text("\n".join(common + add) + "\n", encoding="utf-8")


if only is not None:
    write(ROOT / sys.argv[2], [s for k, s in enumerate(sites) if k in only])
    print([("%d:%08X" % (k, s[0])) for k, s in enumerate(sites) if k in only])
else:
    bits = max(1, (len(sites) - 1).bit_length())
    for b in range(bits):
        chosen = [s for k, s in enumerate(sites) if (k >> b) & 1]
        write(ROOT / ("%s%d" % (sys.argv[2], b)), chosen)
        print("bit %d: %d sites" % (b, len(chosen)))
    (ROOT / (sys.argv[2] + "-sites.txt")).write_text("\n".join("%d %08X" % (k, s[0]) for k, s in enumerate(sites)) + "\n")
