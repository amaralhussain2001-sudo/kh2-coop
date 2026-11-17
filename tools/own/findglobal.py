"""List the places in the game program that read or write a global word.
python -I findglobal.py <elf> <hex address> [<hex address> ...]
A place is a load / store / addiu whose 16-bit offset is the low half of the address, where a `lui reg,high`
of the right high half was seen in the 24 instructions before it (same register as the base)."""
import struct, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-v2"))
import mips

e = mips.Elf(sys.argv[1])
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
MEM = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x28: "sb", 0x29: "sh", 0x2B: "sw", 0x09: "addiu",
       0x31: "lwc1", 0x39: "swc1", 0x37: "ld", 0x3F: "sd"}
for arg in sys.argv[2:]:
    addr = int(arg, 16)
    lo = addr & 0xFFFF
    hi = ((addr + 0x8000) >> 16) & 0xFFFF
    print("== %08X" % addr)
    for i, w in enumerate(words):
        op = w >> 26
        if op not in MEM or (w & 0xFFFF) != lo:
            continue
        base = (w >> 21) & 31
        ok = False
        for j in range(i - 1, max(i - 25, -1), -1):
            x = words[j]
            if (x >> 26) == 0x0F and ((x >> 16) & 31) == base:
                ok = (x & 0xFFFF) == hi
                break
        if ok:
            pc = va + 4 * i
            print("%08X  %s" % (pc, mips.dis(w, pc)))
