"""Lane B75: where do two screenshots differ? Prints the bounding box of the differing pixels.  usage: img_diff.py a.png b.png [...pairs]"""
import sys
from PIL import Image, ImageChops

args = sys.argv[1:]
for i in range(0, len(args), 2):
    a, b = Image.open(args[i]).convert("RGB"), Image.open(args[i + 1]).convert("RGB")
    d = ImageChops.difference(a, b)
    box = d.getbbox()
    n = sum(1 for px in d.getdata() if px != (0, 0, 0)) if box else 0
    print(args[i].replace("\\", "/").rsplit("/", 1)[1], "size", a.size, "differing box", box, "pixels", n)
