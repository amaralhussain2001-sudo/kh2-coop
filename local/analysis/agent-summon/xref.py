import sys, struct
sys.path.insert(0,r"C:\Users\PC FORCE\Desktop\New folder (3)\tools\lane-a")
import mips
e=mips.Elf(r"C:\Users\PC FORCE\Desktop\New folder (3)\local\iso-files\SLPM_666.75")
va,off,fs=e.segs[0]
target=int(sys.argv[1],16)
hi=(target+0x8000)>>16; lo=target-(hi<<16)
n=fs//4
W=[struct.unpack_from("<I",e.data,off+4*i)[0] for i in range(n)]
for i,w in enumerate(W):
    op=w>>26
    if op in (0x23,0x2B,0x24,0x28,0x25,0x29,0x09) and (w&0xFFFF)==(lo&0xFFFF):
        rs=(w>>21)&31
        # look back up to 12 words for lui rs,hi
        for k in range(1,40):
            if i-k<0: break
            p=W[i-k]
            if p>>26==0x0F and ((p>>16)&31)==rs:
                if (p&0xFFFF)==hi: print("%08X %s"%(va+4*i, mips.dis(w,va+4*i)))
                break
