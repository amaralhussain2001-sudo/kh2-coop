"""Lane V2: list the places that ask for a controller (jal 0x00167F18) and then test a given button bit.

  python -I tools/lane-v2/padscan.py <hexmask> [<window>]

For every call of the controller getter, prints the call site, the controller index if it is loaded in the delay
slot or just before (li a0,N / move a0,zero), and every "andi x,y,<mask>" within <window> instructions after it.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from disw import loader  # noqa: E402

GETTER = 0x00167F18


def main():
    mask = int(sys.argv[1], 16)
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    word = loader()
    jal = 0x0C000000 | (GETTER >> 2)
    a = 0x00100000
    hits = 0
    total = 0
    while True:
        w = word(a)
        if w is None:
            break
        if w == jal:
            total += 1
            idx = "?"
            for back in (4, -4, -8):
                d = word(a + back)
                if d == 0x0000202D:
                    idx = "0"
                    break
                if d is not None and (d >> 16) == 0x2404:
                    idx = str(d & 0xFFFF)
                    break
            found = []
            for k in range(2, window + 2):
                d = word(a + 4 * k)
                if d is None:
                    break
                if (d >> 26) == 0x0C and (d & 0xFFFF) == mask:
                    found.append("%08X" % (a + 4 * k))
            if found:
                hits += 1
                print("call at %08X  controller %s  mask test at %s" % (a, idx, ", ".join(found)))
        a += 4
    print("%d calls of the controller getter, %d followed by a test of mask 0x%X" % (total, hits, mask))


if __name__ == "__main__":
    main()
