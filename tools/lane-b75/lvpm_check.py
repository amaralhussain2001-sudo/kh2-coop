"""Lane B75: read the level table (lvpm) of 00battle.bin and compare with lane C's dump.  usage: lvpm_check.py <00battle.bin> <lvpm.yml>"""
import re
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
import bar  # noqa: E402

blob = open(sys.argv[1], "rb").read()
for e in bar.entries(blob):
    if e["name"].strip("\0").lower() in ("lvpm", "enmp", "btlv"):
        print(e["name"], "type", e["type"], "size", e["size"])
ent = bar.find(blob, "lvpm", bar.TYPE_LIST)
t = blob[ent["offset"]:ent["offset"] + ent["size"]]
print("first bytes:", t[:24].hex())
yml = [int(m.group(1)) for m in re.finditer(r"HpMultiplier: (\d+)", open(sys.argv[2], encoding="utf-8").read())]
for head in (0, 4, 8):
    for step in (12, 16):
        n = (len(t) - head) // step
        vals = [struct.unpack_from("<H", t, head + step * i)[0] for i in range(min(n, 99))]
        if vals == yml[:len(vals)] and len(vals) == 99:
            print("layout: header", head, "bytes, entry", step, "bytes, HpMultiplier = first u16; 99 levels match lane C's dump")
