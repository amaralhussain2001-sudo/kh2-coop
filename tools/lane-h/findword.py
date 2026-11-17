"""Lane H: where in the game program is a given 32-bit word stored (for example a function's address in a table)?
Prints each place with the words around it.   python -I tools/lane-h/findword.py <elf> <hex> [before] [after]"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
val = int(sys.argv[2], 16)
before = int(sys.argv[3]) if len(sys.argv) > 3 else 4
after = int(sys.argv[4]) if len(sys.argv) > 4 else 8
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
for i, w in enumerate(words):
    if w == val:
        print("0x%08X:" % (va + 4 * i), " ".join("%08X" % words[k] for k in range(max(0, i - before), min(len(words), i + after))))
