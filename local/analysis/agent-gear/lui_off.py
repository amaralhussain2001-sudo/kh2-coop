import sys, re
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
hi = int(sys.argv[1], 16); offs = set(int(x) for x in sys.argv[2].split(","))
lo, top = 0x00100000, 0x00340000
for a in range(lo, top, 4):
    w = e.word(a)
    if w is None: continue
    if (w >> 26) == 0x0F and (w & 0xFFFF) == hi:
        r = (w >> 16) & 31
        for k in range(1, 12):
            w2 = e.word(a + 4*k)
            op = w2 >> 26; rs = (w2 >> 21) & 31; imm = w2 & 0xFFFF
            simm = imm - 0x10000 if imm & 0x8000 else imm
            if rs == r and simm in offs:
                print("%08X %s   <- %08X" % (a + 4*k, mips.dis(w2, a + 4*k), a))
