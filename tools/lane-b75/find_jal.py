"""Lane B75: list every jal to the given routines, with the start of the enclosing routine (previous 'addiu sp,sp,-N').

  python -I tools/lane-b75/find_jal.py <elf> <targetHex> [targetHex ...]
"""
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 2)[0] + "/lane-a")
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
for t in [int(x, 16) for x in sys.argv[2:]]:
    jal = (0x03 << 26) | ((t >> 2) & 0x3FFFFFF)
    jmp = (0x02 << 26) | ((t >> 2) & 0x3FFFFFF)
    sites = [i for i, w in enumerate(words) if w in (jal, jmp)]
    print("calls to 0x%08X: %d" % (t, len(sites)))
    for i in sites:
        k = i
        while k > 0 and not ((words[k] >> 16) == 0x27BD and (words[k] & 0x8000)):
            k -= 1
        print("  0x%08X  in routine 0x%08X%s" % (va + 4 * i, va + 4 * k, "  (jump)" if words[i] == jmp else ""))
