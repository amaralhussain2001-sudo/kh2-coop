"""Read-only: every call (jal) of given routines of the main program, in the main program and in the five module files
(local/analysis/lane-s3/ovl/*.x, loaded at 0x01F18000), and every load / store of a given absolute address.
  python -I tools/own/ovl_calls.py <routineHex,routineHex,...> [<addressHex,...>]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

routines = [int(x, 16) for x in sys.argv[1].split(",")]
addrs = [int(x, 16) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else []
jals = {(3 << 26) | (r >> 2): r for r in routines}
files = [("main", None)] + [(f.stem, f) for f in sorted((ROOT / "local" / "analysis" / "lane-s3" / "ovl").glob("*.x"))]
elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
for name, f in files:
    if f is None:
        va, off, fs = elf.segs[0]
        words = struct.unpack_from("<%dI" % (fs // 4), elf.data, off)
        base = va
    else:
        d = f.read_bytes()
        words = struct.unpack_from("<%dI" % (len(d) // 4), d, 0)
        base = 0x01F18000
    for i, w in enumerate(words):
        pc = base + 4 * i
        if w in jals:
            print("%-16s %08X  jal %08X" % (name, pc, jals[w]))
        if (w >> 26) == 0x0F and addrs:
            rt, hi = (w >> 16) & 31, (w & 0xFFFF) << 16
            for k in range(1, 8):
                if i + k >= len(words):
                    break
                v = words[i + k]
                if ((v >> 21) & 31) != rt:
                    continue
                imm = v & 0xFFFF
                s = imm - 0x10000 if imm & 0x8000 else imm
                t = (hi + s) & 0xFFFFFFFF
                if t in addrs:
                    print("%-16s %08X  %s   (address %08X)" % (name, base + 4 * (i + k), mips.dis(v, base + 4 * (i + k)), t))
                break
