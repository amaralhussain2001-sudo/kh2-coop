"""List the script engine's call tables in the main program's data: runs of (routine address, input count word)
pairs. For one routine address: the table it is in and its index there.
  python -I tools/own/trap_tables.py [<routineHex> ...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))


def word(a):
    for va, off, fs in elf.segs:
        if va <= a < va + fs:
            return struct.unpack_from("<I", elf.data, off + a - va)[0]
    return None


def is_pair(a):
    r, c = word(a), word(a + 4)
    return r is not None and c is not None and 0x00100000 <= r < 0x00300000 and (c & 0xBFFFFFFF) < 32


tables, a = [], 0x00340000
while a < 0x00380000:
    if is_pair(a):
        s = a
        while is_pair(a):
            a += 8
        if (a - s) // 8 >= 4:
            tables.append((s, (a - s) // 8))
    else:
        a += 4
want = [int(x, 16) for x in sys.argv[1:]]
for s, n in tables:
    hit = [(i, w) for w in want for i in range(n) if word(s + 8 * i) == w]
    if not want:
        print("%08X  %d entries" % (s, n))
    for i, w in hit:
        print("%08X is entry %d of the table at %08X (%d entries), inputs %08X" % (w, i, s, n, word(s + 8 * i + 4)))
