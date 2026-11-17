"""Lane E: small MIPS (R5900 subset) text assembler with labels, for the patch routines.

    words = assemble(base_address, source_text, symbols)

Source: one instruction per line, "label:" lines, "#" comments. Operands: registers by name, numbers (decimal or
0x..), symbols from the dict, %hi(sym) / %lo(sym) for lui + signed-offset pairs, memory operands "off(reg)".
Branch and jump targets may be labels, symbols or numbers. No delay-slot magic: write the delay slot yourself.
"""
import re
import struct

R = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
     "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]
RN = {n: i for i, n in enumerate(R)}

I_FMT = {"addiu": 0x09, "ori": 0x0D, "xori": 0x0E, "andi": 0x0C, "slti": 0x0A, "sltiu": 0x0B, "daddiu": 0x19}
MEM = {"lb": 0x20, "lh": 0x21, "lw": 0x23, "lbu": 0x24, "lhu": 0x25, "sb": 0x28, "sh": 0x29, "sw": 0x2B,
       "ld": 0x37, "sd": 0x3F, "lwc1": 0x31, "swc1": 0x39}
R3 = {"addu": 0x21, "subu": 0x23, "and": 0x24, "or": 0x25, "xor": 0x26, "nor": 0x27, "slt": 0x2A, "sltu": 0x2B,
      "daddu": 0x2D, "movz": 0x0A, "movn": 0x0B}
SH = {"sll": 0x00, "srl": 0x02, "sra": 0x03}
BR2 = {"beq": 0x04, "bne": 0x05, "beql": 0x14, "bnel": 0x15}
BR1 = {"blez": 0x06, "bgtz": 0x07}
REGIMM = {"bltz": 0, "bgez": 1}
FPU3 = {"add.s": 0, "sub.s": 1, "mul.s": 2, "div.s": 3}
FCMP = {"c.eq.s": 0x32, "c.lt.s": 0x34, "c.le.s": 0x36}


class AsmError(Exception):
    pass


def _freg(s):
    if not re.fullmatch(r"f\d+", s):
        raise AsmError("float register expected: " + s)
    return int(s[1:])


def assemble(base, text, symbols=None):
    symbols = dict(symbols or {})
    lines = []
    pc = base
    for raw in text.split("\n"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):", line)
        if m:
            if m.group(1) in symbols:
                raise AsmError("duplicate label " + m.group(1))
            symbols[m.group(1)] = pc
            continue
        lines.append((pc, line))
        pc += 4

    def val(tok):
        tok = tok.strip()
        m = re.fullmatch(r"%(hi|lo)\((.+)\)", tok)
        if m:
            v = val(m.group(2))
            lo = v & 0xFFFF
            if m.group(1) == "lo":
                return lo - 0x10000 if lo & 0x8000 else lo
            return ((v + 0x8000) >> 16) & 0xFFFF
        neg = tok.startswith("-")
        t = tok[1:] if neg else tok
        if t in symbols:
            v = symbols[t]
        else:
            try:
                v = int(t, 0)
            except ValueError:
                raise AsmError("unknown symbol or number: " + tok)
        return -v if neg else v

    def reg(tok):
        tok = tok.strip()
        if tok not in RN:
            raise AsmError("register expected: " + tok)
        return RN[tok]

    def mem(tok):
        m = re.fullmatch(r"(.*)\((\w+)\)", tok.strip())
        if not m:
            raise AsmError("memory operand expected: " + tok)
        return val(m.group(1) or "0"), reg(m.group(2))

    def imm16(v, signed=True):
        if signed and not -0x8000 <= v <= 0x7FFF:
            raise AsmError("immediate out of signed 16-bit range: %d" % v)
        if not signed and not 0 <= v <= 0xFFFF:
            raise AsmError("immediate out of unsigned 16-bit range: %d" % v)
        return v & 0xFFFF

    out = []
    for pc, line in lines:
        parts = line.split(None, 1)
        op = parts[0]
        a = [x.strip() for x in parts[1].split(",")] if len(parts) > 1 else []
        try:
            if op == "nop":
                w = 0
            elif op == "lui":
                w = (0x0F << 26) | (reg(a[0]) << 16) | imm16(val(a[1]), signed=False)
            elif op in I_FMT:
                v = val(a[2])
                w = (I_FMT[op] << 26) | (reg(a[1]) << 21) | (reg(a[0]) << 16) | \
                    imm16(v, signed=op in ("addiu", "slti", "sltiu", "daddiu"))
            elif op == "li":      # li reg, small constant (signed 16-bit)
                w = (0x09 << 26) | (reg(a[0]) << 16) | imm16(val(a[1]))
            elif op in MEM:
                off, base_r = mem(a[1])
                rt = _freg(a[0]) if op in ("lwc1", "swc1") else reg(a[0])
                w = (MEM[op] << 26) | (base_r << 21) | (rt << 16) | imm16(off)
            elif op in R3:
                w = (reg(a[1]) << 21) | (reg(a[2]) << 16) | (reg(a[0]) << 11) | R3[op]
            elif op == "move":
                w = (reg(a[1]) << 21) | (reg(a[0]) << 11) | 0x2D
            elif op in SH:
                w = (reg(a[1]) << 16) | (reg(a[0]) << 11) | ((val(a[2]) & 31) << 6) | SH[op]
            elif op in BR2:
                t = val(a[2])
                w = (BR2[op] << 26) | (reg(a[0]) << 21) | (reg(a[1]) << 16) | imm16((t - (pc + 4)) >> 2)
            elif op in BR1:
                t = val(a[1])
                w = (BR1[op] << 26) | (reg(a[0]) << 21) | imm16((t - (pc + 4)) >> 2)
            elif op in REGIMM:
                t = val(a[1])
                w = (1 << 26) | (reg(a[0]) << 21) | (REGIMM[op] << 16) | imm16((t - (pc + 4)) >> 2)
            elif op == "b":
                t = val(a[0])
                w = (0x04 << 26) | imm16((t - (pc + 4)) >> 2)
            elif op in ("j", "jal"):
                t = val(a[0])
                w = ((2 if op == "j" else 3) << 26) | ((t >> 2) & 0x3FFFFFF)
            elif op == "jr":
                w = (reg(a[0]) << 21) | 0x08
            elif op == "jalr":
                w = (reg(a[0]) << 21) | (31 << 11) | 0x09
            elif op == "mtc1":
                w = (0x11 << 26) | (4 << 21) | (reg(a[0]) << 16) | (_freg(a[1]) << 11)
            elif op == "mfc1":
                w = (0x11 << 26) | (0 << 21) | (reg(a[0]) << 16) | (_freg(a[1]) << 11)
            elif op in FPU3:
                w = (0x11 << 26) | (0x10 << 21) | (_freg(a[2]) << 16) | (_freg(a[1]) << 11) | (_freg(a[0]) << 6) | FPU3[op]
            elif op == "abs.s":
                w = (0x11 << 26) | (0x10 << 21) | (_freg(a[1]) << 11) | (_freg(a[0]) << 6) | 0x05
            elif op == "mov.s":
                w = (0x11 << 26) | (0x10 << 21) | (_freg(a[1]) << 11) | (_freg(a[0]) << 6) | 0x06
            elif op in FCMP:
                w = (0x11 << 26) | (0x10 << 21) | (_freg(a[1]) << 16) | (_freg(a[0]) << 11) | FCMP[op]
            elif op in ("bc1t", "bc1f"):
                t = val(a[0])
                w = (0x11 << 26) | (8 << 21) | ((1 if op == "bc1t" else 0) << 16) | imm16((t - (pc + 4)) >> 2)
            elif op == ".word":
                w = val(a[0]) & 0xFFFFFFFF
            else:
                raise AsmError("unknown instruction")
        except AsmError as e:
            raise AsmError("%08X  %s : %s" % (pc, line, e))
        out.append(w & 0xFFFFFFFF)
    return out, symbols


if __name__ == "__main__":
    import sys
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import mips
    words, syms = assemble(0x000F0300, "start:\n lui t7,%hi(0x0034E948)\n lw t6,%lo(0x0034E948)(t7)\n beq t6,zero,start\n nop\n j 0x001781E8\n sw zero,%lo(0x0034E948)(t7)")
    for i, w in enumerate(words):
        print("%08X  %08X  %s" % (0x000F0300 + 4 * i, w, mips.dis(w, 0x000F0300 + 4 * i)))
