"""Lane D: list every load/store in the game program that uses a given offset (e.g. 0x264), to see how a
structure field is used.  python -I tools/lane-d/scan_off.py <elf> <offsetHex> [<offsetHex> ...]
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-a"))
from mips import Elf, dis, MEM  # noqa: E402


def main():
    e = Elf(sys.argv[1])
    offs = {int(x, 16) for x in sys.argv[2:]}
    for va, off, fs in e.segs:
        n = fs // 4
        words = struct.unpack_from(f"<{n}I", e.data, off)
        for i, w in enumerate(words):
            op = w >> 26
            if op in MEM:
                imm = w & 0xFFFF
                simm = imm - 0x10000 if imm & 0x8000 else imm
                if simm in offs:
                    pc = va + 4 * i
                    print(f"{pc:08X}  {dis(w, pc)}")


if __name__ == "__main__":
    main()
