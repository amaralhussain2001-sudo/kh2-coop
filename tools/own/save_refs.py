"""Read-only (ninth round, the user's answer D: a second bag needs room in the save data): EVERY ABSOLUTE ADDRESS INSIDE THE
SAVE DATA BLOCK (0x0032BB30, 0x10FC0 bytes) THAT THE PROGRAM'S CODE BUILDS, in the main program and in the five
module files (local/analysis/lane-s3/ovl/*.x, each loaded at 0x01F18000). An address is "built" by a `lui r,hi`
followed within 12 instructions by an instruction that uses r with a 16-bit number (addiu / ori / a load / a
store). It does NOT see an access through a pointer that was handed over (save pointer + offset): for a stretch
that is to be called free, the routines that take the save pointer must be read too.
  python -I tools/own/save_refs.py                     the list: offset, address, how often, where first
  python -I tools/own/save_refs.py <fromHex> <toHex>    only the references into save + from .. save + to, each place"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

SAVE, SIZE = 0x0032BB30, 0x10FC0
LOADS = {0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2E, 0x31, 0x37, 0x39, 0x3F, 0x1A, 0x1B, 0x1E, 0x1F}


def scan(name, words, base):
    """-> list of (address, pc, name)"""
    out = []
    reg = {}                                   # register -> (hi value, pc of the lui)
    for i, w in enumerate(words):
        pc = base + 4 * i
        op, rs, rt, imm = w >> 26, (w >> 21) & 31, (w >> 16) & 31, w & 0xFFFF
        simm = imm - 0x10000 if imm & 0x8000 else imm
        if op == 0x0F:                         # lui
            reg[rt] = (imm << 16, pc)
            continue
        if rs in reg and pc - reg[rs][1] <= 48:
            hi = reg[rs][0]
            if op in (0x09, 0x19) or op in LOADS:          # addiu / daddiu / a load / a store
                a = (hi + simm) & 0xFFFFFFFF
                if SAVE <= a < SAVE + SIZE:
                    out.append((a, pc, name))
            elif op == 0x0D:                               # ori
                a = hi | imm
                if SAVE <= a < SAVE + SIZE:
                    out.append((a, pc, name))
        # a register that is written loses its lui
        if op in (0x09, 0x19, 0x0D, 0x0C, 0x0E, 0x0A, 0x0B) or op in (0x20, 0x21, 0x23, 0x24, 0x25, 0x37, 0x27):
            if rt in reg and rt != rs:
                del reg[rt]
            elif rt in reg and rt == rs and op not in (0x09, 0x19, 0x0D):
                del reg[rt]
        elif op == 0:
            rd = (w >> 11) & 31
            if rd in reg:
                del reg[rd]
        elif op in (2, 3):                     # a jump or a call: the temporaries are gone after the delay slot
            pass
    return out


def main():
    elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
    refs = []
    for va, off, fs in elf.segs:
        n = fs // 4
        words = struct.unpack_from("<%dI" % n, elf.data, off)
        refs += scan("main", words, va)
    for f in sorted((ROOT / "local" / "analysis" / "lane-s3" / "ovl").glob("*.x")):
        d = f.read_bytes()
        words = struct.unpack_from("<%dI" % (len(d) // 4), d, 0)
        refs += scan(f.stem, words, 0x01F18000)
    if len(sys.argv) >= 3:
        lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
        for a, pc, name in sorted(refs):
            if lo <= a - SAVE <= hi:
                print("save + %05X (%08X)  at %08X in %s" % (a - SAVE, a, pc, name))
        return
    seen = {}
    for a, pc, name in refs:
        seen.setdefault(a, []).append((pc, name))
    print("%d addresses inside the save block are built by the code (%d places)" % (len(seen), len(refs)))
    for a in sorted(seen):
        pcs = seen[a]
        print("save + %05X (%08X)  %3d places, first %08X in %s; modules: %s" % (
            a - SAVE, a, len(pcs), pcs[0][0], pcs[0][1], ", ".join(sorted({n for _p, n in pcs}))))


main()
