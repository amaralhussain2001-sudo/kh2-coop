"""Lane B75: is the Scan ability (item 0x008A) in the heroes' starting data? Lists the table entries of 00battle.bin
that contain the 16-bit value 0x008A or 0x808A (= equipped).  usage: find_scan_ability.py <00battle.bin>"""
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
import bar  # noqa: E402

blob = open(sys.argv[1], "rb").read()
for e in bar.entries(blob):
    t = blob[e["offset"]:e["offset"] + e["size"]]
    hits = [i for i in range(0, len(t) - 1, 2) if struct.unpack_from("<H", t, i)[0] in (0x008A, 0x808A)]
    name = e["name"].strip("\0")
    if hits:
        print("%-6s size %6d: %d hits at %s" % (name, e["size"], len(hits), " ".join("0x%X" % h for h in hits[:12])))
    if name.lower() == "plrp":
        n = struct.unpack_from("<I", t, 4)[0]
        print("  plrp: version %d, %d entries, entry size %d" % (struct.unpack_from("<I", t, 0)[0], n, (len(t) - 8) // max(n, 1)))
        size = (len(t) - 8) // max(n, 1)
        for h in hits:
            k = (h - 8) // size
            o = 8 + k * size
            print("    hit 0x%X is in entry %d, field offset 0x%X; entry head: %s" % (h, k, h - o, t[o:o + 12].hex()))
