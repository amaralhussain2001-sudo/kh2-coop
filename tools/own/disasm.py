"""Read-only: disassemble a range of the game program, or print data words.
  python -I tools/own/disasm.py <startHex> <count>          instructions
  python -I tools/own/disasm.py -w <startHex> <count>       data words
  python -I tools/own/disasm.py -c <targetHex>              every jal to the target"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = e.segs[0]


def word(a):
    return struct.unpack_from("<I", e.data, off + a - va)[0]


if sys.argv[1] == "-w":
    a, n = int(sys.argv[2], 16), int(sys.argv[3], 0)
    for i in range(n):
        print("%08X  %08X" % (a + 4 * i, word(a + 4 * i)))
elif sys.argv[1] == "-c":
    t = int(sys.argv[2], 16)
    w = (3 << 26) | ((t >> 2) & 0x3FFFFFF)
    words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
    print(" ".join("%08X" % (va + 4 * i) for i, x in enumerate(words) if x == w))
else:
    a, n = int(sys.argv[1], 16), int(sys.argv[2], 0)
    for i in range(n):
        pc = a + 4 * i
        print("%08X  %s" % (pc, mips.dis(word(pc), pc)))
