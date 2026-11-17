"""Lane S1: look for pointers between the two heroes and the boss in the object dumps saved by s1rc.py.

  python -I tools/lane-s1/s1rcdump.py <test-name> [--max 40]

Each dump (taken when a hero's action number changed) holds hero object (0xB80 bytes), twin object (0xB80) and the
first 0x1000 bytes of the boss object. For each dump it lists the offsets of 32-bit words that hold
  in the boss:  the hero's address, the twin's address
  in the hero:  the boss's address, the twin's address
  in the twin:  the boss's address, the hero's address
Offsets that are the same in every dump are printed once at the end ("always"); the per-dump lines show only the
ones that come and go, next to the two heroes' action numbers at that moment.
"""
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def offs(blob, value):
    out = []
    for i in range(0, len(blob) - 3, 4):
        if struct.unpack_from("<I", blob, i)[0] == value:
            out.append(i)
    return out


def main():
    test = sys.argv[1]
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 40
    d = ROOT / "local" / "tests" / test / "rcdump"
    files = sorted(d.glob("*.bin"))
    recs = []
    for f in files:
        m = re.match(r"(\d+)_H([0-9A-F]+)_T([0-9A-F]+)_B([0-9A-F]+)_a([0-9A-F]+)_([0-9A-F]+)", f.stem)
        if not m:
            continue
        t, h, tw, b = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16), int(m.group(4), 16)
        blob = f.read_bytes()
        hb, tb, bb = blob[:0xB80], blob[0xB80:0x1700], blob[0x1700:]
        rec = {"t": t, "acts": (m.group(5), m.group(6)), "boss": b,
               "B>H": offs(bb, h), "B>T": offs(bb, tw), "H>B": offs(hb, b), "H>T": offs(hb, tw),
               "T>B": offs(tb, b), "T>H": offs(tb, h)}
        recs.append(rec)
    if not recs:
        print("%s: no dumps" % test)
        return
    keys = ["B>H", "B>T", "H>B", "H>T", "T>B", "T>H"]
    always = {k: set(recs[0][k]) for k in keys}
    for r in recs:
        for k in keys:
            always[k] &= set(r[k])
    print("== %s: %d dumps. Legend: B = boss object, H = player 1's hero, T = twin; 'B>H' = offsets in the boss "
          "that hold the hero's address" % (test, len(recs)))
    print("   always: " + "; ".join("%s %s" % (k, " ".join("+%X" % o for o in sorted(always[k])) or "-") for k in keys))
    t0 = recs[0]["t"]
    for r in recs[:mx]:
        parts = []
        for k in keys:
            extra = [o for o in r[k] if o not in always[k]]
            if extra:
                parts.append("%s %s" % (k, " ".join("+%X" % o for o in extra)))
        print("   +%6d ms  H act %3s T act %3s  boss %X | %s" % (r["t"] - t0, r["acts"][0], r["acts"][1], r["boss"],
                                                             "; ".join(parts) or "(nothing beyond 'always')"))


if __name__ == "__main__":
    main()
