"""Disassemble a range of the game program (no Ghidra).  python -I tools/lane-v1/dis.py <loHex> <hiHex>"""
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
a = lo
while a < hi:
    w = e.word(a)
    print("%08X  %08X  %s" % (a, w, mips.dis(w, a)))
    a += 4
