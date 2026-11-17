"""TEST ONLY: <base patch> + "Donald and Goofy carry two Potions each". At session frame 4850, once, each helper's
character block gets the count byte of his item places (block + 0x12) = 2 and a Potion (item 1) in the first two
places (block + 0x34, 2 bytes each). Blocks: Donald 0x0032E134, Goofy 0x0032E248. Same on both PCs.
  python -I tools/own/make_hitemkit.py <baseDir> <outDir>"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_hitemkit.py): at frame 4850 both helpers get 2 item places with a Potion each; for tests only.")
c = (4850 - 152) & 0xFFFF
for line in ("0032E146,extended,00000002", "1032E168,extended,00000001", "1032E16A,extended,00000001",
             "0032E25A,extended,00000002", "1032E27C,extended,00000001", "1032E27E,extended,00000001"):
    lines.append("patch=1,EE,E001%04X,extended,0034D4BC" % c)
    lines.append("patch=1,EE," + line)
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(lines), "lines")
