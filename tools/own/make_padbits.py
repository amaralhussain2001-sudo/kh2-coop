"""TEST ONLY: bit-coded search for the controller read of a text box.
<base patch> + "getter call sites whose index has bit b set read controller 2" (lane A's bisect idea), six folders.
  python -I tools/own/make_padbits.py <baseDir> <outPrefix> [only: idx,idx,...]
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "lane-a"))
import bisect as lane_a_bisect  # noqa: E402  (tools/lane-a/bisect.py)

NAME = "SLPM-66675_F266B00B.pnach"
base = ROOT / sys.argv[1]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
used = {int(l.split(",")[2], 16) for l in text if l.startswith("patch=")}
sites = lane_a_bisect.sites(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
usable = [(i, c, w) for i, (c, w) in enumerate(sites) if w is not None and w not in used and c not in used and i != 14]
print("usable sites:", len(usable), "skipped:", [i for i, (c, w) in enumerate(sites) if (i, c, w) not in usable])
if len(sys.argv) > 3:
    idx = {int(x) for x in sys.argv[3].split(",")}
    out = ROOT / sys.argv[2]
    out.mkdir(parents=True, exist_ok=True)
    add = ["patch=1,EE,%08X,word,24040001" % w for i, c, w in usable if i in idx]
    (out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
    print(out, [("%d:%08X" % (i, c)) for i, c, w in usable if i in idx])
else:
    for b in range(6):
        out = ROOT / ("%s%d" % (sys.argv[2], b))
        out.mkdir(parents=True, exist_ok=True)
        add = ["patch=1,EE,%08X,word,24040001" % w for i, c, w in usable if (i >> b) & 1]
        (out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
        print(out.name, len(add), "sites")
