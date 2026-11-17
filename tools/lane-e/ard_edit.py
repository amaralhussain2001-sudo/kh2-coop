"""Lane E: move / turn entities inside a room file (ARD) without changing its size.

  python -I tools/lane-e/ard_edit.py <in.ard> <out.ard> <edit> [<edit> ...]
  edit = group:spawnPoint:entity:x:y:z[:rotY]      e.g.  m_00:0:0:-470:0:-550:-1.57
  edit = swap:group:spawnPoint:entityA:entityB     exchange two entity records (changes the creation order)
Only the position (and rotation Y) floats of existing entity records are rewritten, or two records exchanged.
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ard import bar_entries  # noqa: E402


def entity_offset(data, group, sp_index, ent_index):
    for typ, name, off, size in bar_entries(data):
        if typ != 12 or name != group:
            continue
        p = off + 8
        count = struct.unpack_from("<i", data, off + 4)[0]
        for i in range(count):
            n_ent, n_act, n_walk, n_ret, n_sig = struct.unpack_from("<hhhhh", data, p + 4)
            ents = p + 0x2C
            if i == sp_index:
                if ent_index >= n_ent:
                    raise SystemExit("entity index out of range")
                return ents + 0x40 * ent_index
            q = ents + 0x40 * n_ent + 0x40 * n_act
            for _ in range(n_walk):
                cnt = struct.unpack_from("<h", data, q + 2)[0]
                q += 8 + 12 * cnt
            p = q + 0x10 * n_ret + 8 * n_sig
        raise SystemExit("spawn point index out of range")
    raise SystemExit("group not found: " + group)


def main():
    data = bytearray(pathlib.Path(sys.argv[1]).read_bytes())
    for e in sys.argv[3:]:
        f = e.split(":")
        if f[0] == "swap":
            a = entity_offset(data, f[1], int(f[2]), int(f[3]))
            b = entity_offset(data, f[1], int(f[2]), int(f[4]))
            ra, rb = bytes(data[a:a + 0x40]), bytes(data[b:b + 0x40])
            data[a:a + 0x40], data[b:b + 0x40] = rb, ra
            print("swapped %s[%s] entities %s and %s" % (f[1], f[2], f[3], f[4]))
            continue
        o = entity_offset(data, f[0], int(f[1]), int(f[2]))
        obj = struct.unpack_from("<i", data, o)[0]
        struct.pack_into("<3f", data, o + 4, float(f[3]), float(f[4]), float(f[5]))
        if len(f) > 6:
            struct.pack_into("<f", data, o + 0x14, float(f[6]))
        print("%s[%s] entity %s (object 0x%X) -> pos (%s, %s, %s)%s" % (
            f[0], f[1], f[2], obj, f[3], f[4], f[5], " rotY " + f[6] if len(f) > 6 else ""))
    out = pathlib.Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes(data))


if __name__ == "__main__":
    main()
