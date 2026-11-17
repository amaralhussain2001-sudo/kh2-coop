"""TEST ONLY: <base patch> + ONE-TIME writes at one video frame (a one-frame conditional line on the game's frame
counter 0x0034D4BC = session frame - 152, as make_healkit.py does). The same lines on both PCs. Never part of the
real patch.
  python -I tools/own/make_once.py <basePatchDir> <outDir> <sessionFrame> ADDR=VALUE [ADDR=VALUE ...]     (hex)
  VALUE with 4 hex digits = a 16-bit write, with 8 = a 32-bit write, with 2 = one byte.
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out, frame = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_once.py %s): for tests only." % " ".join(sys.argv[3:]))
count = (frame - 152) & 0xFFFF
for a in sys.argv[4:]:
    addr, val = a.split("=")
    kind = {2: 0x00000000, 4: 0x10000000, 8: 0x20000000}[len(val)]
    lines.append("patch=1,EE,E001%04X,extended,%08X" % (count, 0x0034D4BC))
    lines.append("patch=1,EE,%08X,extended,%08X" % (kind | int(addr, 16), int(val, 16)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(sys.argv) - 4, "writes at frame", frame)
