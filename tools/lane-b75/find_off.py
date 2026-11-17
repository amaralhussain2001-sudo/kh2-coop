"""Lane B75: list loads/stores that use a given 16-bit offset (e.g. the HP gauge's fields).

  python -I tools/lane-b75/find_off.py <elf> <offset> [loHex hiHex]
"""
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 2)[0] + "/lane-a")
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
offv = int(sys.argv[2], 0) & 0xFFFF
va, off, fs = e.segs[0]
lo = int(sys.argv[3], 16) if len(sys.argv) > 3 else va
hi = int(sys.argv[4], 16) if len(sys.argv) > 4 else va + fs
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
for i, w in enumerate(words):
    pc = va + 4 * i
    if not lo <= pc < hi:
        continue
    op = w >> 26
    if op in mips.MEM and (w & 0xFFFF) == offv:
        print("0x%08X  %s" % (pc, mips.dis(w, pc)))
