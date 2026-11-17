"""Scan the whole main program file (code and data) for one 32-bit word, for example a routine's address in a table.
  python -I tools/own/find_word.py <hex32> [...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
for arg in sys.argv[1:]:
    want = int(arg, 16)
    n = 0
    for va, off, fs in elf.segs:
        for pc in range(va, va + fs - 3, 4):
            if struct.unpack_from("<I", elf.data, off + pc - va)[0] == want:
                print("%08X holds %08X" % (pc, want))
                n += 1
    # a "lui + addiu / ori" pair that makes the address
    va, off, fs = elf.segs[0]
    hi, lo = want >> 16, want & 0xFFFF
    hi2 = (hi + 1) & 0xFFFF if lo >= 0x8000 else hi
    for pc in range(va, min(va + fs, 0x00300000) - 3, 4):
        w = struct.unpack_from("<I", elf.data, off + pc - va)[0]
        if (w >> 26) in (9, 13) and (w & 0xFFFF) == lo:
            for q in range(pc - 4, pc - 40, -4):
                w2 = struct.unpack_from("<I", elf.data, off + q - va)[0]
                if (w2 >> 26) == 15 and (w2 & 0xFFFF) in (hi, hi2):
                    print("%08X makes %08X (lui at %08X)" % (pc, want, q))
                    n += 1
                    break
    print(n, "places for %08X" % want)
