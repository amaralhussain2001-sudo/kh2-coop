import sys, struct
sys.path.insert(0,r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e=mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
va,off,fs=e.segs[0]
d=e.data
want={3:0x40000000,8:2,11:3,13:3,14:0x40000001,18:6,29:0x40000004,34:0x40000000,70:2,71:2,157:3}
for base in range(va, va+fs-8*200, 4):
    ok=True
    for i,v in want.items():
        if struct.unpack_from("<I",d,off+base-va+8*i+4)[0]!=v: ok=False;break
    if ok:
        print("base %08X"%base)
        for i in (3,8,11,18,29,34,102,157,181,184):
            print(i, "%08X %08X"%struct.unpack_from("<II",d,off+base-va+8*i))
