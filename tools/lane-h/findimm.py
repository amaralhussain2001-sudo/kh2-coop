"""Lane E: list instructions in the game program whose 16-bit immediate equals one of the given values
(addiu/ori/xori/slti/sltiu/andi/li forms).  python -I findimm.py <elf> <hex> [<hex> ...]"""
import struct, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips
e = mips.Elf(sys.argv[1])
vals = {int(x, 16) for x in sys.argv[2:]}
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
for i, w in enumerate(words):
    op = w >> 26
    if op in (0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x18, 0x19) and (w & 0xFFFF) in vals:
        pc = va + 4 * i
        print("%08X  %s" % (pc, mips.dis(w, pc)))
