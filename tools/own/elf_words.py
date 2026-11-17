"""Read words of the game's main program (the ELF on disc) at an address, for reading tables.
  python -I tools/own/elf_words.py <addrHex> [count]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
a = int(sys.argv[1], 16)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for i in range(n):
    pc = a + 4 * i
    for va, off, fs in elf.segs:
        if va <= pc < va + fs:
            print("%08X  %08X" % (pc, struct.unpack_from("<I", elf.data, off + pc - va)[0]))
            break
    else:
        print("%08X  (not in the file)" % pc)
