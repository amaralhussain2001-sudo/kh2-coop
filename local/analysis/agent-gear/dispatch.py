import sys, struct
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
t = int(sys.argv[1], 16); n = int(sys.argv[2]) if len(sys.argv) > 2 else 14
va, off, fs = e.segs[0]
words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
jal = (3 << 26) | ((t >> 2) & 0x3FFFFFF)
for i, w in enumerate(words):
    if w == jal:
        pc = va + 4*i
        for k in range(1, n):
            s = mips.dis(words[i+k], pc + 4*k)
            if (s.startswith("jr ") and s != "jr ra") or s.startswith("jalr"):
                print("%08X -> %08X %s" % (pc, pc+4*k, s))
                break
