"""Merge lane, TEST ONLY: <base patch> + one line that keeps one unit slot's HP at 1, so the first hit is lethal.
Identical on both PCs, so a linked session stays in sync. Never part of the real game patch.

  python -I tools/merge/make_testdie.py <basePatchDir> <outDir> [slotAddressHex]
Default slot: 0x01C6C4E8 = the second slot handed out, which is player 1's hero on the twin-everywhere discs
(the twin is built first and has the first slot, 0x01C6C750).
"""
import pathlib
import sys

base, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
slot = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x01C6C4E8
lines = [x for x in (base / "SLPM-66675_F266B00B.pnach").read_text().splitlines() if x.strip()]
lines.append("comment=MERGE LANE TEST ONLY: HP of the unit slot at 0x%08X held at 1 (first hit is lethal)." % slot)
lines.append("patch=1,EE,%08X,word,00000001" % slot)
out.mkdir(parents=True, exist_ok=True)
(out / "SLPM-66675_F266B00B.pnach").write_text(chr(10).join(lines) + chr(10))
print(out, len(lines), "lines")
