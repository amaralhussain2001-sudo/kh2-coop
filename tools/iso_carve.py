"""Copy named root files out of a PS2 ISO (read-only on the ISO). Usage: iso_carve.py <iso> <outdir> NAME [NAME...]"""
import sys, struct, os
iso, out, names = sys.argv[1], sys.argv[2], [n.upper() for n in sys.argv[3:]]
os.makedirs(out, exist_ok=True)
f = open(iso, 'rb')
f.seek(16*2048); pvd = f.read(2048); assert pvd[1:6] == b'CD001'
root = pvd[156:190]
lba, size = struct.unpack('<I', root[2:6])[0], struct.unpack('<I', root[10:14])[0]
f.seek(lba*2048); d = f.read(size); i = 0
while i < len(d):
    ln = d[i]
    if ln == 0:
        i = (i//2048+1)*2048; continue
    rec = d[i:i+ln]; i += ln
    nm = rec[33:33+rec[32]].decode('ascii', 'replace').split(';')[0].upper()
    if nm in names:
        flba, fsize = struct.unpack('<I', rec[2:6])[0], struct.unpack('<I', rec[10:14])[0]
        f.seek(flba*2048); left = fsize
        with open(os.path.join(out, nm), 'wb') as o:
            while left:
                b = f.read(min(left, 1 << 24)); o.write(b); left -= len(b)
        print(nm, 'lba', flba, 'size', fsize)
