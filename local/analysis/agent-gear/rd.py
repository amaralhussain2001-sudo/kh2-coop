import sys, struct
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
a = int(sys.argv[1], 16); n = int(sys.argv[2]) if len(sys.argv) > 2 else 16
kind = sys.argv[3] if len(sys.argv) > 3 else "w"
if kind == "w":
    for i in range(n):
        print("%08X  %08X" % (a + 4*i, e.word(a + 4*i)))
elif kind == "d":
    for i in range(n):
        lo = e.word(a + 8*i); hi = e.word(a + 8*i + 4)
        print("%08X  %08X%08X" % (a + 8*i, hi, lo))
