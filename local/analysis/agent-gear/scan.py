import sys
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
lo = int(sys.argv[1], 16); hi = int(sys.argv[2], 16); pat = sys.argv[3]
import re
rx = re.compile(pat)
for a in range(lo, hi, 4):
    s = mips.dis(e.word(a), a)
    if rx.search(s):
        print("%08X  %s" % (a, s))
