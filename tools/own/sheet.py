"""Contact sheet of a test's pictures (small tiles, both players), so one Read shows a whole run.
  python -I tools/own/sheet.py <testDir> [width] [frames,frames,...]
Writes <testDir>/sheet.png
"""
import pathlib
import sys
from PIL import Image, ImageDraw

d = pathlib.Path(sys.argv[1])
w = int(sys.argv[2]) if len(sys.argv) > 2 else 420
only = {int(x) for x in sys.argv[3].split(",")} if len(sys.argv) > 3 else None
frames = sorted({int(p.stem.split("_f")[1]) for p in d.glob("p?_f*.png")})
if only:
    frames = [f for f in frames if f in only]
tiles = []
for f in frames:
    for pl in (1, 2):
        p = d / ("p%d_f%06d.png" % (pl, f))
        if p.exists():
            im = Image.open(p).convert("RGB")
            h = im.height * w // im.width
            im = im.resize((w, h))
            ImageDraw.Draw(im).text((6, 4), "P%d f%d" % (pl, f), fill=(255, 255, 0))
            tiles.append(im)
cols = 4 if len(tiles) > 4 else max(2, len(tiles))
rows = (len(tiles) + cols - 1) // cols
h = tiles[0].height
sheet = Image.new("RGB", (cols * w, rows * h))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(d / "sheet.png")
print(d / "sheet.png", sheet.size)
