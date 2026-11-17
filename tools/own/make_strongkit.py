"""TEST ONLY: <base patch> + "strong heroes": Strength and Defense of Sora's character record written to 150 (the bytes
0x0032E029 / 0x0032E02B, as the kit -snapB-god-strong of v115 had them; both heroes read that record in fights). The same on
both PCs. Never part of the real patch.
  python -I tools/own/make_strongkit.py <baseDir> <outDir>"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
used = {l.split(",")[2].upper() for l in lines if l.startswith("patch=")}
add = ["comment=TEST KIT (strong heroes: Strength / Defense 150): for tests only.",
       "patch=1,EE,0032E029,byte,96", "patch=1,EE,0032E02B,byte,96"]
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines + add) + "\n", encoding="utf-8")
print("written", out / NAME)
