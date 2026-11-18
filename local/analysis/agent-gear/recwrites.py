# menu code: find "lw rX,580(rY)" (record pointer of a unit slot) and stores through rX within 24 instructions
import sys, re
sys.path.insert(0, r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e = mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
lo, hi = 0x00240000, 0x002B4000
for a in range(lo, hi, 4):
    s = mips.dis(e.word(a), a)
    m = re.match(r"lw ([a-z0-9]+),580\(", s)
    if not m: continue
    r = m.group(1)
    hits = []
    regs = {r}
    for k in range(1, 30):
        t = mips.dis(e.word(a + 4*k), a + 4*k)
        mm = re.match(r"(sb|sh|sw|sd) ([a-z0-9]+),(-?\d+)\(([a-z0-9]+)\)", t)
        if mm and mm.group(4) in regs:
            hits.append("%08X %s" % (a + 4*k, t))
        mm2 = re.match(r"(addu|daddu|addiu) ([a-z0-9]+),([a-z0-9]+),([a-z0-9-]+)", t)
        if mm2 and (mm2.group(3) in regs or mm2.group(4) in regs):
            regs.add(mm2.group(2))
        if t.startswith("jr ra"): break
    if hits:
        print("%08X %s :: %s" % (a, s, " | ".join(hits)))
