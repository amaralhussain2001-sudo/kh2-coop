"""Lane N: read class tables and disassemble code from the game program (no emulator needed).

  python -I tools/lane-n/vt.py table <hexaddr> [count]         words of a class table with their offsets
  python -I tools/lane-n/vt.py dis <hexstart> <hexend>          disassembly
  python -I tools/lane-n/vt.py find <hexword> [mask]            code/data addresses holding that word
  python -I tools/lane-n/vt.py calls <hextarget>                every jal/j to the target
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"


def main():
    e = mips.Elf(str(ELF))
    cmd = sys.argv[1]
    if cmd == "table":
        a = int(sys.argv[2], 16)
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        for i in range(n):
            w = e.word(a + 4 * i)
            print(f"+0x{4 * i:03X}  0x{a + 4 * i:08X}: {w:08X}" if w is not None else f"+0x{4 * i:03X} (outside)")
    elif cmd == "dis":
        a, b = int(sys.argv[2], 16), int(sys.argv[3], 16)
        for pc in range(a, b, 4):
            w = e.word(pc)
            print(f"0x{pc:08X}: {w:08X}  {mips.dis(w, pc)}")
    elif cmd == "find":
        want = int(sys.argv[2], 16)
        mask = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xFFFFFFFF
        for va, off, fs in e.segs:
            words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
            for i, w in enumerate(words):
                if w & mask == want & mask:
                    print(f"0x{va + 4 * i:08X}: {w:08X}")
    elif cmd == "calls":
        t = int(sys.argv[2], 16)
        jal = (3 << 26) | ((t >> 2) & 0x3FFFFFF)
        jmp = (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        for va, off, fs in e.segs:
            words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
            for i, w in enumerate(words):
                if w == jal:
                    print(f"0x{va + 4 * i:08X}: jal")
                elif w == jmp:
                    print(f"0x{va + 4 * i:08X}: j")


if __name__ == "__main__":
    main()
