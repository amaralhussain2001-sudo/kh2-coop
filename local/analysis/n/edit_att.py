import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/nprobe.py")
s = p.read_text(encoding="utf-8")
old = """                room = p.r16(0x0032BAE0)"""
new = """                if want_att:   # read-only: attack objects (list head 0x01C60CD8, next at +0xC0) seen for the first time
                    a, n, now = p.r32(0x01C60CD8), 0, set()
                    while a and n < 64:
                        blk = p.read(a, 0xC4)
                        own, own2, grp, num, data = struct.unpack_from("<IIIII", blk, 8)[0], struct.unpack_from("<I", blk, 0xC)[0], struct.unpack_from("<I", blk, 0x14)[0], struct.unpack_from("<I", blk, 0x18)[0], struct.unpack_from("<I", blk, 0x28)[0]
                        now.add(a)
                        if a not in seen_att:
                            typ = p.r8(data + 4) if data else -1
                            names = {u["owner"]: u["role"] for u in us}
                            fh.write("%6d  ATTACK %07X owner %s group %X number %X type %d" % (f, a, names.get(own2, "%07X" % own2), grp, num, typ) + chr(10))
                        a = struct.unpack_from("<I", blk, 0xC0)[0]
                        n += 1
                    for gone in sorted(seen_att - now):
                        fh.write("%6d  ATTACK %07X gone" % (f, gone) + chr(10))
                    seen_att.clear()
                    seen_att.update(now)
                room = p.r16(0x0032BAE0)"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    lines, lastkey, lastf = [], None, -1"""
new = """    lines, lastkey, lastf = [], None, -1
    want_att, seen_att = "--attacks" in sys.argv, set()"""
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("ok")
