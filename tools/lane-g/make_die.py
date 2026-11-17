"""Lane G, TEST ONLY: <base patch> + one line that keeps the heroes' shared HP (unit slot 1) at 1, so the first hit
is lethal. Identical on both PCs, so a linked session stays in sync. Never part of the real game patch.

  python -I tools/lane-g/make_die.py <basePatchDir> <outDir>
"""
import pathlib
import sys

base, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
lines = [l for l in (base / "SLPM-66675_F266B00B.pnach").read_text().splitlines() if l.strip()]
lines.append("comment=LANE G TEST ONLY: shared HP held at 1 (first hit is lethal).")
lines.append("patch=1,EE,01C6C750,word,00000001")
out.mkdir(parents=True, exist_ok=True)
(out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
print(out, len(lines), "lines")
