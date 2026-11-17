"""TEST ONLY: <base patch> + "one party member carries items" (make_hitemkit.py for ANY character block). At a
session frame, once, the member's block in the save data gets the count byte of his item places (block + 0x12)
and an item in each of the first places (block + 0x34, 2 bytes each). Same on both PCs.
Blocks (save + ...; each 0x114 bytes; HYPOTHESIS from the save layout, Sora / Donald / Goofy VERIFIED before):
  Sora 24F0, Donald 2604, Goofy 2718, Mickey 282C, Auron 2940, Mulan 2A54, Aladdin 2B68, Jack Sparrow 2C7C,
  Beast 2D90, Jack Skellington 2EA4, Simba 2FB8, Tron 30CC, Riku 31E0
  python -I tools/own/make_guestitems.py <baseDir> <outDir> <blockHex> [count=2] [item=1] [frame=4850]
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
SAVE = 0x0032BB30
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out, block = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3], 16)
count = int(sys.argv[4]) if len(sys.argv) > 4 else 2
item = int(sys.argv[5]) if len(sys.argv) > 5 else 1
frame = int(sys.argv[6]) if len(sys.argv) > 6 else 4850
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_guestitems.py block %04X: %d places with item %d at frame %d): for tests only."
             % (block, count, item, frame))
c = (frame - 152) & 0xFFFF
a = SAVE + block
writes = ["%08X,extended,%08X" % (a + 0x12, count)]                          # 8-bit write
writes += ["%08X,extended,%08X" % (0x10000000 | (a + 0x34 + 2 * i), item) for i in range(count)]   # 16-bit writes
for w in writes:
    lines.append("patch=1,EE,E001%04X,extended,0034D4BC" % c)
    lines.append("patch=1,EE," + w)
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "block %04X" % block, len(lines), "lines")
