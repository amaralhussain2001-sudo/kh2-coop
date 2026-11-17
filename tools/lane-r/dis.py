"""Lane R: disassemble a range of the game program (read-only).  python -I tools/lane-r/dis.py <hexStart> <hexEnd>"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "merge"))
import make_all  # noqa: E402
import mips  # noqa: E402

word = make_all.load_elf_words()
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
for addr in range(a, b + 1, 4):
    w = word(addr)
    if w is None:
        print("%08X  (outside the program file)" % addr)
        continue
    print("%08X  %08X  %s" % (addr, w, mips.dis(w, addr)))
