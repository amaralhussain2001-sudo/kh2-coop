"""Lane G: find frame counters by comparing two full memory dumps taken a known number of frames apart.

  python -I tools/lane-g/find_counter.py <ramA.bin> <ramB.bin> <frames-apart>
Prints 32-bit words that grew by about <frames> (video frames) or <frames>/2 (game steps), static area only.
"""
import struct
import sys

a = open(sys.argv[1], "rb").read()
b = open(sys.argv[2], "rb").read()
d = int(sys.argv[3])
n = len(a) // 4
wa = struct.unpack("<%dI" % n, a)
wb = struct.unpack("<%dI" % n, b)
for label, target, tol in (("video frames", d, 12), ("game steps", d // 2, 6)):
    print(f"== grew by about {target} ({label})")
    shown = 0
    for i in range(0x00100000 // 4, n):
        diff = (wb[i] - wa[i]) & 0xFFFFFFFF
        if abs(diff - target) <= tol and wa[i] < 0x00400000:
            addr = i * 4
            if addr < 0x00400000 or 0x01C00000 <= addr < 0x01E00000:
                print(f"  0x{addr:08X}: {wa[i]} -> {wb[i]} (+{diff})")
                shown += 1
                if shown > 40:
                    break
