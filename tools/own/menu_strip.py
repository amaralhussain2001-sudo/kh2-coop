"""Read-only: cut the command menu corner out of a run's screenshots and put the cuts side by side.
  python tools/own/menu_strip.py <testDir> <p1|p2> <frame,frame,...> <out.png> [perRow]"""
import pathlib
import sys
from PIL import Image, ImageDraw

d, who, frames, out = pathlib.Path(sys.argv[1]), sys.argv[2], [int(x) for x in sys.argv[3].split(",")], sys.argv[4]
per = int(sys.argv[5]) if len(sys.argv) > 5 else 8
cuts = []
for f in frames:
    p = d / ("%s_f%06d.png" % (who, f))
    if not p.exists():
        continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    c = im.crop((0, int(h * 0.62), int(w * 0.34), h)).resize((210, 176))
    ImageDraw.Draw(c).text((4, 2), "%s f%d" % (who, f), fill=(255, 255, 0))
    cuts.append(c)
rows = (len(cuts) + per - 1) // per
sheet = Image.new("RGB", (210 * per, 176 * rows))
for i, c in enumerate(cuts):
    sheet.paste(c, (210 * (i % per), 176 * (i // per)))
sheet.save(out)
print(out, len(cuts), "cuts")
