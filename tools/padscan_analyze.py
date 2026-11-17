"""Find controller state in the memory dumps of test pad01-scan.

Windows (see tests/scripts/padscan_p1.txt / padscan_p2.txt):
  6500 nothing held | 7700 P2 TRIANGLE | 8900 P2 SQUARE | 10100 P2 L1 | 11300 P2 left stick right
  12500 P1 L1 | 13700 P1 R1
A button word of pad 2 keeps its value in the windows where pad 2 holds no button and differs by exactly one bit
in each of the three button windows (three different bits). Same idea for pad 1 with its two windows.

  python -I tools/padscan_analyze.py <test-out-dir>
"""
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
F = [6500, 7700, 8900, 10100, 11300, 12500, 13700]
R = {f: (d / f"ram_f{f:06d}.bin").read_bytes() for f in F}
N = len(R[6500])


def xor(a, b):
    return (int.from_bytes(a, "little") ^ int.from_bytes(b, "little")).to_bytes(N, "little")


def one_bit(v):
    return v != 0 and v & (v - 1) == 0


def w16(buf, o):
    return buf[o] | (buf[o + 1] << 8)


base = R[6500]
x_tri, x_sq, x_l1 = xor(base, R[7700]), xor(base, R[8900]), xor(base, R[10100])
x_p1l1, x_p1r1 = xor(base, R[12500]), xor(base, R[13700])

print("== pad 2 button words (16-bit, value: idle / TRI / SQ / L1)")
p2 = []
for o in range(0, N - 1, 2):
    a = w16(x_tri, o)
    if not a:
        continue
    b, c = w16(x_sq, o), w16(x_l1, o)
    if one_bit(a) and one_bit(b) and one_bit(c) and len({a, b, c}) == 3:
        if w16(R[11300], o) == w16(base, o) and w16(x_p1l1, o) == 0 and w16(x_p1r1, o) == 0:
            p2.append(o)
            print(f"  0x{o:08X}: {w16(base, o):04X} / {w16(R[7700], o):04X} / {w16(R[8900], o):04X} / {w16(R[10100], o):04X}")

print("== pad 1 button words (16-bit, value: idle / L1 / R1)")
p1 = []
for o in range(0, N - 1, 2):
    a = w16(x_p1l1, o)
    if not a:
        continue
    b = w16(x_p1r1, o)
    if one_bit(a) and one_bit(b) and a != b:
        if all(w16(R[f], o) == w16(base, o) for f in (7700, 8900, 10100, 11300)):
            p1.append(o)
            print(f"  0x{o:08X}: {w16(base, o):04X} / {w16(R[12500], o):04X} / {w16(R[13700], o):04X}")

print("== pad 2 left stick X (byte: 0x7F/0x80 idle, 0xFF in window 11300, idle elsewhere)")
x_lx = xor(base, R[11300])
for o in range(N):
    if x_lx[o] and R[11300][o] == 0xFF and base[o] in (0x7F, 0x80):
        if all(R[f][o] == base[o] for f in (7700, 8900, 10100, 12500, 13700)):
            print(f"  0x{o:08X}: idle {base[o]:02X}")

print("== distances between pad 1 and pad 2 candidates (same layout => same distance repeated)")
from collections import Counter
dist = Counter(b - a for a in p1 for b in p2)
for k, v in dist.most_common(8):
    print(f"  pad2 - pad1 = 0x{k & 0xFFFFFFFF:X} ({k}) x{v}")
