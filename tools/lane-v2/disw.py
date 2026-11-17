"""Lane V2: disassemble words of the game program file (no Ghidra).

  python -I tools/lane-v2/dis.py <start_hex> <count> [<start_hex> <count> ...]
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import mips  # noqa: E402

ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"


def loader():
    data = ELF.read_bytes()
    e_phoff = struct.unpack_from("<I", data, 0x1C)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 0x2A)
    segs = []
    for i in range(e_phnum):
        p_type, p_offset, p_vaddr, _, p_filesz = struct.unpack_from("<IIIII", data, e_phoff + i * e_phentsize)
        if p_type == 1:
            segs.append((p_vaddr, p_offset, p_filesz))

    def word(addr):
        for vaddr, off, size in segs:
            if vaddr <= addr < vaddr + size:
                return struct.unpack_from("<I", data, off + addr - vaddr)[0]
        return None
    return word


def main():
    word = loader()
    a = sys.argv[1:]
    for i in range(0, len(a), 2):
        start, n = int(a[i], 16), int(a[i + 1])
        for k in range(n):
            ad = start + 4 * k
            w = word(ad)
            if w is None:
                print("%08X  (not in file)" % ad)
                continue
            print("%08X  %08X  %s" % (ad, w, mips.dis(w, ad)))
        print()


if __name__ == "__main__":
    main()
