"""TEST ONLY: <base patch> + one conditional test line pair: while the 16-bit value at <condAddr> equals <cond16>,
the word at <addr> is written with <value> every frame (same on both PCs). Never part of the real game patch.
  python -I tools/own/make_pin.py <basePatchDir> <outDir> <condAddrHex> <cond16Hex> <addrHex>=<valueHex> [...]"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
cond_addr, cond16 = int(sys.argv[3], 16), int(sys.argv[4], 16)
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST PIN (tools/own/make_pin.py %s): for tests only." % " ".join(sys.argv[3:]))
for pair in sys.argv[5:]:
    a, v = pair.split("=")
    lines.append("patch=1,EE,E001%04X,extended,%08X" % (cond16, cond_addr))
    lines.append("patch=1,EE,%08X,extended,%08X" % (0x20000000 | int(a, 16), int(v, 16)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(lines), "lines")
