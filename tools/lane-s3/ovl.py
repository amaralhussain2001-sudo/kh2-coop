"""Lane S3: read the overlay code modules (ovl_gumibattle.x, ovl_gumimenu.x, ...), which are raw MIPS code loaded
at 0x01F18000 (the main program's second segment).

  python -I tools/lane-s3/ovl.py calls   <ovl> <targetHex>            list call sites of one routine (with a0 set-up)
  python -I tools/lane-s3/ovl.py dis     <ovl> <startHex> <endHex>    disassemble
  python -I tools/lane-s3/ovl.py jalstat <ovl> [N]                    most-called targets (main program and overlay)
  python -I tools/lane-s3/ovl.py refs    <ovl> <addrHex> [span]       lui/addiu|lw|sw... pairs that form an address
  python -I tools/lane-s3/ovl.py strings <ovl>                        printable strings with their addresses
  python -I tools/lane-s3/ovl.py funcs   <ovl>                        function starts (addiu sp,sp,-N) list
"""
import collections
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lane-a"))
import mips  # noqa: E402

BASE = 0x01F18000


def load(path):
    d = pathlib.Path(path).read_bytes()
    n = len(d) // 4
    return d, list(struct.unpack("<%dI" % n, d[:n * 4]))


def jal_target(w):
    return (w & 0x03FFFFFF) << 2


def cmd_calls(path, target):
    d, ws = load(path)
    enc = (0x03 << 26) | ((target >> 2) & 0x3FFFFFF)
    for i, w in enumerate(ws):
        if w == enc:
            pc = BASE + 4 * i
            ctx = []
            for k in range(max(0, i - 4), min(len(ws), i + 2)):
                ctx.append("%08X: %s" % (BASE + 4 * k, mips.dis(ws[k], BASE + 4 * k)))
            print("call at 0x%08X" % pc)
            for c in ctx:
                print("    " + c)


def cmd_dis(path, a, b):
    d, ws = load(path)
    for pc in range(a, b, 4):
        i = (pc - BASE) // 4
        if 0 <= i < len(ws):
            print("%08X: %08X  %s" % (pc, ws[i], mips.dis(ws[i], pc)))


def cmd_jalstat(path, n=40):
    d, ws = load(path)
    c = collections.Counter()
    for w in ws:
        if w >> 26 == 3:
            c[jal_target(w)] += 1
    main = [(t, k) for t, k in c.items() if t < BASE]
    own = [(t, k) for t, k in c.items() if t >= BASE]
    print("distinct targets: main program %d, overlay %d" % (len(main), len(own)))
    print("-- main program targets")
    for t, k in sorted(main, key=lambda x: -x[1])[:n]:
        print("  0x%08X x%d" % (t, k))
    print("-- overlay targets")
    for t, k in sorted(own, key=lambda x: -x[1])[:n]:
        print("  0x%08X x%d" % (t, k))


def cmd_refs(path, addr, span=0):
    d, ws = load(path)
    hi_reg = {}
    for i, w in enumerate(ws):
        op = w >> 26
        rs, rt, imm = (w >> 21) & 31, (w >> 16) & 31, w & 0xFFFF
        if op == 0x0F:  # lui
            hi_reg[rt] = (imm << 16, i)
            continue
        if op in (0x09, 0x0D) or op in mips.MEM:
            if rs in hi_reg and i - hi_reg[rs][1] <= 6:
                base = hi_reg[rs][0]
                val = (base + (mips.s16(imm) if op != 0x0D else imm)) & 0xFFFFFFFF
                if addr <= val <= addr + span:
                    print("0x%08X: %s   -> 0x%08X" % (BASE + 4 * i, mips.dis(w, BASE + 4 * i), val))


def cmd_strings(path):
    d, ws = load(path)
    for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
        print("0x%08X %s" % (BASE + m.start(), m.group().decode("ascii")[:100]))


def cmd_funcs(path):
    d, ws = load(path)
    n = 0
    for i, w in enumerate(ws):
        if (w >> 16) == 0x27BD and (w & 0x8000):  # addiu sp,sp,-N
            n += 1
            print("0x%08X frame %d" % (BASE + 4 * i, 0x10000 - (w & 0xFFFF)))
    print("functions:", n)


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "calls":
        cmd_calls(sys.argv[2], int(sys.argv[3], 16))
    elif c == "dis":
        cmd_dis(sys.argv[2], int(sys.argv[3], 16), int(sys.argv[4], 16))
    elif c == "jalstat":
        cmd_jalstat(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 40)
    elif c == "refs":
        cmd_refs(sys.argv[2], int(sys.argv[3], 16), int(sys.argv[4], 16) if len(sys.argv) > 4 else 0)
    elif c == "strings":
        cmd_strings(sys.argv[2])
    elif c == "funcs":
        cmd_funcs(sys.argv[2])
