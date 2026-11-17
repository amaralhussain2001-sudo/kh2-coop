"""TEST ONLY: <base patch> + four lines that change WHERE a jump test disc goes after New Game, without building
a new disc. The disc test-s1-tt137 jumps to "TT, program 137"; its jump record (start room tt01, event program)
is in memory at 0x01C56310 from about session frame 3680 (found with tools/own/jumpfind_probe.py; world word
+6, program word +12, the fade word 0x4002 at +14). The lines write another world and program into it while
it still holds the disc's own values. Same on both PCs. Never part of the real patch.
  python -I tools/own/make_jumpkit.py <baseDir> <outDir> <worldNumberHex> <programDecimal> [recordAddrHex] [--type1]
  --type1: a Type 1 jump (area 0, entrance 0, the save's own programs); world 0F program 0 = the world map.
World numbers: 02 TT, 04 HB, 05 BB, 06 HE, 07 AL, 08 MU, 09 PO, 0A LK, 0B LM, 0C DC, 0D WI, 0E NM, 10 CA, 11 TR, 12 EH."""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
world, prog = int(sys.argv[3], 16), int(sys.argv[4])
pos = [a for a in sys.argv[1:] if not a.startswith("--")]
rec = int(pos[4], 16) if len(pos) > 4 else 0x01C56310
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_jumpkit.py world %02X program %d): for tests only." % (world, prog))
t1 = "--type1" in sys.argv
lines.append("patch=1,EE,E0%02X4002,extended,%08X" % (4 if t1 else 3, rec + 14))    # the fade word of the jump record
lines.append("patch=1,EE,E0%02X0089,extended,%08X" % (3 if t1 else 2, rec + 12))    # still the disc's own program (137)
if "--type1" in sys.argv:                       # a "Type 1" jump (free roam with the save's programs), e.g. the world map 0F
    lines.append("patch=1,EE,%08X,extended,%08X" % (0x10000000 | (rec + 4), 1))
lines.append("patch=1,EE,%08X,extended,%08X" % (0x10000000 | (rec + 6), world))
lines.append("patch=1,EE,%08X,extended,%08X" % (0x10000000 | (rec + 12), prog))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "world %02X program %d" % (world, prog))
