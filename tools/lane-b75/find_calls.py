"""Lane B75: list calls (jal) to given routines whose a1 is loaded with a given constant near the call.

  python -I tools/lane-b75/find_calls.py <elf> <a1 constant | -1 = any> <targetHex> [targetHex ...]
"""
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 2)[0] + "/lane-a")
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
const = int(sys.argv[2], 0)
targets = [int(x, 16) for x in sys.argv[3:]]
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
for t in targets:
    jal = (0x03 << 26) | ((t >> 2) & 0x3FFFFFF)
    sites = [i for i, w in enumerate(words) if w == jal]
    print("calls to 0x%08X: %d" % (t, len(sites)))
    for i in sites:
        hit = None
        for k in [i + 1] + list(range(i - 1, i - 6, -1)):
            w = words[k]
            # addiu a1,zero,imm  /  ori a1,zero,imm
            if (w >> 16) in (0x2405, 0x3405):
                hit = w & 0xFFFF
                break
        if const < 0 or hit == const:
            print("  0x%08X  a1=%s" % (va + 4 * i, hit))
