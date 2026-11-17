"""Lane E: read a room file (ARD = BAR archive) in plain Python: spawn groups with their entities, event
activators (the invisible trigger volumes) and teleport fields.

  python -I tools/lane-e/ard.py <file.ard> [groupName ...]      (no group names = every spawn group)
"""
import struct
import sys


def bar_entries(data):
    assert data[:4] == b"BAR\x01", "not a BAR file"
    count = struct.unpack_from("<I", data, 4)[0]
    res = []
    for i in range(count):
        typ, dup, name, off, size = struct.unpack_from("<HH4sII", data, 0x10 + 0x10 * i)
        res.append((typ, name.rstrip(b"\0").decode("ascii", "replace"), off, size))
    return res


def spawn_points(blob):
    if len(blob) < 8:
        return []
    typ, count = struct.unpack_from("<ii", blob, 0)
    res = []
    p = 8
    for _ in range(max(count, 0)):
        (t, flag, sid, n_ent, n_act, n_walk, n_ret, n_sig, _r0e, _r10, _r14, _r18,
         place, door, world, unk1f, unk20, unk24, _unk28) = struct.unpack_from("<BBhhhhhhhiiiBBBBiii", blob, p)
        p += 0x2C
        ents = []
        for _ in range(n_ent):
            e = struct.unpack_from("<i6fBBhiihhhhBBhiii", blob, p)
            p += 0x40
            ents.append(dict(obj=e[0], pos=e[1:4], rot=e[4:7], stype=e[7], sarg=e[8], serial=e[9], a1=e[10], a2=e[11],
                             rc=e[12], delay=e[13], cmd=e[14], rng=e[15]))
        acts = []
        for _ in range(n_act):
            a = struct.unpack_from("<hh9fihBBiiii", blob, p)
            p += 0x40
            acts.append(dict(shape=a[0], option=a[1], pos=a[2:5], scale=a[5:8], rot=a[8:11], flags=a[11], type=a[12],
                             onbg=a[13], offbg=a[14]))
        for _ in range(n_walk):
            serial, cnt, fl, wid, _r = struct.unpack_from("<hhBBh", blob, p)
            p += 8 + 12 * cnt
        p += 0x10 * n_ret
        sigs = []
        for _ in range(n_sig):
            sigs.append(struct.unpack_from("<HHB3x", blob, p))
            p += 8
        res.append(dict(type=t, flag=flag, id=sid, place=place, door=door, world=world, unk1f=unk1f, unk20=unk20,
                        unk24=unk24, ents=ents, acts=acts, sigs=sigs))
    return res


def main():
    data = open(sys.argv[1], "rb").read()
    want = set(sys.argv[2:])
    for typ, name, off, size in bar_entries(data):
        if typ != 12 or (want and name not in want):
            continue
        sps = spawn_points(data[off:off + size])
        print("== %s (%d bytes, %d spawn points)" % (name, size, len(sps)))
        for i, sp in enumerate(sps):
            print("  [%d] type %d flag %d id %d  teleport place %d door %d world %d unk %d  unk20 %08X unk24 %08X" % (
                i, sp["type"], sp["flag"], sp["id"], sp["place"], sp["door"], sp["world"], sp["unk1f"],
                sp["unk20"] & 0xFFFFFFFF, sp["unk24"] & 0xFFFFFFFF))
            for e in sp["ents"]:
                print("      ent obj %04X pos (%.1f %.1f %.1f) rotY %.2f stype %d sarg %d serial %d a1 %d a2 %d" % (
                    e["obj"], e["pos"][0], e["pos"][1], e["pos"][2], e["rot"][1], e["stype"], e["sarg"], e["serial"],
                    e["a1"], e["a2"]))
            for a in sp["acts"]:
                print("      ACTIVATOR shape %d option %d pos (%.1f %.1f %.1f) scale (%.1f %.1f %.1f) rot (%.2f %.2f %.2f) flags %X type %d onbg %d offbg %d" % (
                    a["shape"], a["option"], a["pos"][0], a["pos"][1], a["pos"][2], a["scale"][0], a["scale"][1], a["scale"][2],
                    a["rot"][0], a["rot"][1], a["rot"][2], a["flags"] & 0xFFFFFFFF, a["type"], a["onbg"], a["offbg"]))
            for s in sp["sigs"]:
                print("      signal %s" % (s,))


if __name__ == "__main__":
    main()
