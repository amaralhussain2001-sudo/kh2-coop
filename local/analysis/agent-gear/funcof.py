# find the function start (addiu sp,sp,-N) before an address, then list callers of it
import sys, struct, subprocess
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
va, off, fs = e.segs[0]
words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
def start_of(a):
    b = a
    while b > a - 0x1000:
        w = e.word(b)
        if (w & 0xFFFF0000) == 0x27BD0000 and (w & 0x8000):
            # previous must be jr ra / nop region typically
            return b
        b -= 4
    return None
def callers(t):
    jal = (3 << 26) | ((t >> 2) & 0x3FFFFFF); jj = (2 << 26) | ((t >> 2) & 0x3FFFFFF)
    return [va + 4*i for i, w in enumerate(words) if w in (jal, jj)]
for x in sys.argv[1:]:
    a = int(x, 16); s = start_of(a)
    cs = callers(s) if s else []
    # also data pointers
    ptrs = [va + 4*i for i, w in enumerate(words) if w == s]
    print("%08X in func %08X  callers %s  ptrs %s" % (a, s or 0, " ".join("%08X" % c for c in cs[:8]), " ".join("%08X" % p for p in ptrs[:6])))
