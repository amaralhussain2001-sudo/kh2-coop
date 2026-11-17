"""Lane A: scan the game program for code that addresses a memory range through lui + (addiu | load | store).

  python -I tools/lane-a/elfscan.py <elf> <lo_hex> <hi_hex> [window]

Prints: code address, kind (addiu/load/store + width), register, target address. No Ghidra needed.
"""
import struct
import sys

LOADS = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x27: "lwu", 0x37: "ld", 0x31: "lwc1",
         0x1E: "lq", 0x1A: "ldl", 0x1B: "ldr", 0x22: "lwl", 0x26: "lwr"}
STORES = {0x28: "sb", 0x29: "sh", 0x2B: "sw", 0x3F: "sd", 0x39: "swc1", 0x1F: "sq"}


def load_elf(path):
    data = open(path, "rb").read()
    assert data[:4] == b"\x7fELF"
    e_entry, e_phoff = struct.unpack_from("<II", data, 0x18)
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 0x2A)
    segs = []
    for i in range(e_phnum):
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from(
            "<IIIIIIII", data, e_phoff + i * e_phentsize)
        if p_type == 1:
            segs.append((p_vaddr, p_offset, p_filesz, p_memsz, p_flags))
    return data, e_entry, segs


def main():
    data, entry, segs = load_elf(sys.argv[1])
    lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
    window = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    print(f"entry 0x{entry:08X}")
    for s in segs:
        print(f"segment vaddr 0x{s[0]:08X} off 0x{s[1]:X} filesz 0x{s[2]:X} memsz 0x{s[3]:X} flags {s[4]}")
    hits = []
    for vaddr, off, filesz, memsz, flags in segs:
        n = filesz // 4
        words = struct.unpack_from(f"<{n}I", data, off)
        for i, w in enumerate(words):
            if (w >> 26) != 0x0F:
                continue
            reg = (w >> 16) & 31
            upper = (w & 0xFFFF) << 16
            # only lui values that can reach the range with a signed 16-bit offset
            if not (upper - 0x8000 <= hi and upper + 0x7FFF >= lo):
                continue
            for j in range(i + 1, min(n, i + 1 + window)):
                x = words[j]
                op = x >> 26
                rs = (x >> 21) & 31
                rt = (x >> 16) & 31
                imm = x & 0xFFFF
                simm = imm - 0x10000 if imm & 0x8000 else imm
                if rs == reg and (op in LOADS or op in STORES or op == 0x09):
                    tgt = (upper + simm) & 0xFFFFFFFF
                    if lo <= tgt <= hi:
                        kind = "addiu" if op == 0x09 else LOADS.get(op) or STORES.get(op)
                        hits.append((vaddr + 4 * j, kind, tgt, vaddr + 4 * i))
                # register overwritten?
                if op == 0x0F and rt == reg:
                    break
                if op in (0x09, 0x0D, 0x0C, 0x0A, 0x0B, 0x0E) and rt == reg and rs != reg:
                    break
                if op in LOADS and rt == reg:
                    break
                if op == 0 and ((x >> 11) & 31) == reg and (x & 0x3F) not in (0x08, 0x09):
                    break
    seen = set()
    for a, kind, tgt, luia in sorted(hits):
        if (a, tgt) in seen:
            continue
        seen.add((a, tgt))
        print(f"0x{a:08X}  {kind:6s} -> 0x{tgt:08X}   (lui at 0x{luia:08X})")
    print("hits:", len(seen))


if __name__ == "__main__":
    main()
