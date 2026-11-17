"""Print the handler address of a script engine call (trap) from the game's two call tables
(group 0 at 0x0034D8B0, group 1 at 0x0034DD00, 8 bytes an entry; the first word is the routine).
  python -I tools/own/trap_addr.py <group> <number> [<group> <number> ...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
BASE = {0: 0x0034D8B0, 1: 0x0034DD00}
a = sys.argv[1:]
for i in range(0, len(a), 2):
    g, n = int(a[i]), int(a[i + 1])
    addr = BASE[g] + 8 * n
    for va, off, fs in elf.segs:
        if va <= addr < va + fs:
            w0, w1 = struct.unpack_from("<2I", elf.data, off + addr - va)
            print("trap (%d, %d): table %08X -> routine %08X, second word %08X" % (g, n, addr, w0, w1))
