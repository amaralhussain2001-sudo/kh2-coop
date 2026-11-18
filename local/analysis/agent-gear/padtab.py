import sys
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
names = {0x0001: "SELECT", 0x0008: "START", 0x0010: "UP", 0x0020: "RIGHT", 0x0040: "DOWN", 0x0080: "LEFT",
         0x0100: "L2", 0x0200: "R2", 0x0400: "L1", 0x0800: "R1", 0x1000: "TRI", 0x2000: "O", 0x4000: "X",
         0x8000: "SQ", 0x0002: "L3", 0x0004: "R3"}
def q(a): return e.word(a) | (e.word(a+4) << 32)
a = int(sys.argv[1], 16); end = int(sys.argv[2], 16)
while a < end:
    m = q(a); v = q(a+8)
    nm = "+".join(n for b, n in sorted(names.items()) if m & b)
    print("%08X mask %016X (%s)  -> logical %016X" % (a, m, nm, v))
    if m == 0: print("---- end")
    a += 16
