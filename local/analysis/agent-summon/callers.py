import sys
sys.path.insert(0,r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips, struct
e=mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
va,off,fs=e.segs[0]
targets=[int(x,16) for x in sys.argv[1:]]
for a in range(va, va+fs, 4):
    w=struct.unpack_from("<I",e.data,off+a-va)[0]
    op=w>>26
    if op in (2,3):
        t=((a+4)&0xF0000000)|((w&0x3FFFFFF)<<2)
        if t in targets:
            print("%08X %s -> %08X"%(a,"jal" if op==3 else "j  ",t))
