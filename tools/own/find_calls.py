"""List the places in the game's main program that call (jal / j) one routine, with a few lines before each.
  python -I tools/own/find_calls.py <targetHex> [linesBefore] [linesAfter]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = elf.segs[0]
t = int(sys.argv[1], 16)
before = int(sys.argv[2]) if len(sys.argv) > 2 else 6
after = int(sys.argv[3]) if len(sys.argv) > 3 else 1
enc = {(3 << 26) | ((t >> 2) & 0x3FFFFFF): "jal", (2 << 26) | ((t >> 2) & 0x3FFFFFF): "j"}
n = 0
for pc in range(0x00100000, 0x00340000, 4):
    if off + pc - va + 4 > len(elf.data):
        break
    w = struct.unpack_from("<I", elf.data, off + pc - va)[0]
    if w in enc:
        n += 1
        print("---- %08X (%s)" % (pc, enc[w]))
        for q in range(pc - 4 * before, pc + 4 * after + 4, 4):
            x = struct.unpack_from("<I", elf.data, off + q - va)[0]
            print("%s %08X  %s" % (">" if q == pc else " ", q, mips.dis(x, q)))
print(n, "places")
