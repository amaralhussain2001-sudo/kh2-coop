"""Lane J goal 3: decode the six spawn entries that are not in the usual layout (rooms al08 and po10).

Layout worked out from the bytes (files dumped by `LaneJ rawspawn` into local/analysis/lane-j/oldspawn):

 A) "placement list"  (al08 m_00, al08 m_20, po10 m_00)
      u32 count
      count x { u16 entity_count (1), u16 id, u16 ?, u16 ?, u32 ?   (12 bytes)
                entity_count x 0x100-byte record:
                    u32 object id, float x, float y, float z, float rotation_y, 4 bytes (type/arg/flags),
                    ..., 0xFFFF at +0x20, rest zero }
 B) "zone list"       (al08 m_10, al08 m_11, po10 m_10)
      u32 count
      count x 44 bytes { 16-byte header, float x, y, z, float size_x, size_y, size_z, float rotation_y }
    No objects in these: they are boxes (exits or triggers).

  python -I tools/lane-j/old_layout.py <folder with the .bin files> <objentry.txt>
"""
import pathlib
import re
import struct
import sys

folder, objfile = pathlib.Path(sys.argv[1]), sys.argv[2]
names = {}
for line in open(objfile, errors="replace"):
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        names[int(m.group(1), 16)] = (m.group(2), m.group(3))

for f in sorted(folder.glob("*.bin")):
    b = f.read_bytes()
    count = struct.unpack_from("<I", b, 0)[0]
    print(f"== {f.stem}: {len(b)} bytes, first word {count}")
    if len(b) == 4 + count * 44:
        for i in range(count):
            o = 4 + i * 44
            x, y, z, sx, sy, sz, rot = struct.unpack_from("<7f", b, o + 16)
            print(f"   zone {i}: header {b[o:o + 16].hex()}  position ({x:.1f}, {y:.1f}, {z:.1f})  size ({sx:.1f}, {sy:.1f}, {sz:.1f})  rotation {rot:.2f}")
        continue
    pos, ok = 4, True
    for i in range(count):
        if pos + 12 > len(b):
            ok = False
            break
        n, gid = struct.unpack_from("<HH", b, pos)
        hdr = b[pos:pos + 12].hex()
        pos += 12
        for k in range(n):
            if pos + 0x100 > len(b):
                ok = False
                break
            obj, x, y, z, rot = struct.unpack_from("<I4f", b, pos)
            extra = b[pos + 20:pos + 28].hex()
            typ, model = names.get(obj, ("?", "?"))
            print(f"   block {i} (id {gid}, header {hdr}) entity {k}: object 0x{obj:04X} {model} [{typ}]  position ({x:.1f}, {y:.1f}, {z:.1f})  rotation {rot:.2f}  next bytes {extra}")
            pos += 0x100
    print("   parsed to the end:", ok and pos == len(b))
