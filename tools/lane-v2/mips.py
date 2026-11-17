"""Lane A: tiny MIPS (R5900 subset) disassembler + assembler helpers. Enough for reading short routines and
writing small hooks. Not a full instruction set.

  python -I tools/lane-a/mips.py dis <elf> <startHex> <endHex>
"""
import struct
import sys

R = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
     "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]
RN = {n: i for i, n in enumerate(R)}

I_OPS = {0x08: "addi", 0x09: "addiu", 0x0A: "slti", 0x0B: "sltiu", 0x0C: "andi", 0x0D: "ori", 0x0E: "xori",
         0x18: "daddi", 0x19: "daddiu"}
MEM = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x27: "lwu", 0x28: "sb", 0x29: "sh",
       0x2B: "sw", 0x37: "ld", 0x3F: "sd", 0x1E: "lq", 0x1F: "sq", 0x31: "lwc1", 0x39: "swc1",
       0x22: "lwl", 0x26: "lwr", 0x2A: "swl", 0x2E: "swr", 0x1A: "ldl", 0x1B: "ldr", 0x2C: "sdl", 0x2D: "sdr"}
BR = {0x04: "beq", 0x05: "bne", 0x06: "blez", 0x07: "bgtz", 0x14: "beql", 0x15: "bnel", 0x16: "blezl", 0x17: "bgtzl"}
SPEC = {0x20: "add", 0x21: "addu", 0x22: "sub", 0x23: "subu", 0x24: "and", 0x25: "or", 0x26: "xor", 0x27: "nor",
        0x2A: "slt", 0x2B: "sltu", 0x2D: "daddu", 0x2F: "dsubu", 0x0A: "movz", 0x0B: "movn"}
SHIFT = {0x00: "sll", 0x02: "srl", 0x03: "sra", 0x38: "dsll", 0x3A: "dsrl", 0x3B: "dsra", 0x3C: "dsll32",
         0x3E: "dsrl32", 0x3F: "dsra32"}
SHIFTV = {0x04: "sllv", 0x06: "srlv", 0x07: "srav"}


def s16(x):
    return x - 0x10000 if x & 0x8000 else x


def dis(w, pc):
    op = w >> 26
    rs, rt, rd, sa, fn = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
    imm = w & 0xFFFF
    if w == 0:
        return "nop"
    if op == 0:
        if fn in SPEC:
            return f"{SPEC[fn]} {R[rd]},{R[rs]},{R[rt]}"
        if fn in SHIFT:
            return f"{SHIFT[fn]} {R[rd]},{R[rt]},{sa}"
        if fn in SHIFTV:
            return f"{SHIFTV[fn]} {R[rd]},{R[rt]},{R[rs]}"
        if fn == 0x08:
            return f"jr {R[rs]}"
        if fn == 0x09:
            return f"jalr {R[rs]}"
        if fn == 0x18:
            return f"mult {R[rs]},{R[rt]}" + (f" -> {R[rd]}" if rd else "")
        if fn == 0x1A:
            return f"div {R[rs]},{R[rt]}"
        if fn == 0x10:
            return f"mfhi {R[rd]}"
        if fn == 0x12:
            return f"mflo {R[rd]}"
        if fn == 0x0C:
            return "syscall"
        return f".word 0x{w:08X} (special {fn:02X})"
    if op == 1:
        names = {0: "bltz", 1: "bgez", 2: "bltzl", 3: "bgezl", 0x10: "bltzal", 0x11: "bgezal"}
        return f"{names.get(rt, 'regimm?')} {R[rs]},0x{(pc + 4 + (s16(imm) << 2)) & 0xFFFFFFFF:08X}"
    if op == 2:
        return f"j 0x{((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2):08X}"
    if op == 3:
        return f"jal 0x{((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2):08X}"
    if op in BR:
        t = (pc + 4 + (s16(imm) << 2)) & 0xFFFFFFFF
        if op in (0x06, 0x07, 0x16, 0x17):
            return f"{BR[op]} {R[rs]},0x{t:08X}"
        return f"{BR[op]} {R[rs]},{R[rt]},0x{t:08X}"
    if op in I_OPS:
        if op in (0x0C, 0x0D, 0x0E):
            return f"{I_OPS[op]} {R[rt]},{R[rs]},0x{imm:X}"
        return f"{I_OPS[op]} {R[rt]},{R[rs]},{s16(imm)}"
    if op == 0x0F:
        return f"lui {R[rt]},0x{imm:X}"
    if op in MEM:
        reg = f"f{rt}" if op in (0x31, 0x39) else R[rt]
        return f"{MEM[op]} {reg},{s16(imm)}({R[rs]})"
    if op == 0x11:
        if rs == 0:
            return f"mfc1 {R[rt]},f{rd}"
        if rs == 4:
            return f"mtc1 {R[rt]},f{rd}"
        if rs == 8:
            return f"bc1{'t' if rt & 1 else 'f'}{'l' if rt & 2 else ''} 0x{(pc + 4 + (s16(imm) << 2)) & 0xFFFFFFFF:08X}"
        return f"cop1 0x{w:08X}"
    return f".word 0x{w:08X} (op {op:02X})"


class Elf:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        phoff = struct.unpack_from("<I", self.data, 0x1C)[0]
        phentsize, phnum = struct.unpack_from("<HH", self.data, 0x2A)
        self.segs = []
        for i in range(phnum):
            t, off, va, pa, fs, ms, fl, al = struct.unpack_from("<IIIIIIII", self.data, phoff + i * phentsize)
            if t == 1:
                self.segs.append((va, off, fs))

    def word(self, addr):
        for va, off, fs in self.segs:
            if va <= addr < va + fs:
                return struct.unpack_from("<I", self.data, off + addr - va)[0]
        return None


# ---- assembler helpers (return 32-bit words) ----
def _i(op, rs, rt, imm):
    return (op << 26) | (RN[rs] << 21) | (RN[rt] << 16) | (imm & 0xFFFF)


def lui(rt, imm): return _i(0x0F, "zero", rt, imm)
def addiu(rt, rs, imm): return _i(0x09, rs, rt, imm)
def ori(rt, rs, imm): return _i(0x0D, rs, rt, imm)
def andi(rt, rs, imm): return _i(0x0C, rs, rt, imm)
def lw(rt, off, rs): return _i(0x23, rs, rt, off)
def sw(rt, off, rs): return _i(0x2B, rs, rt, off)
def lbu(rt, off, rs): return _i(0x24, rs, rt, off)
def lhu(rt, off, rs): return _i(0x25, rs, rt, off)
def sd(rt, off, rs): return _i(0x3F, rs, rt, off)
def ld(rt, off, rs): return _i(0x37, rs, rt, off)
def beq(rs, rt, pc, target): return _i(0x04, rs, rt, (target - (pc + 4)) >> 2)
def bne(rs, rt, pc, target): return _i(0x05, rs, rt, (target - (pc + 4)) >> 2)
def j(target): return (0x02 << 26) | ((target >> 2) & 0x3FFFFFF)
def jal(target): return (0x03 << 26) | ((target >> 2) & 0x3FFFFFF)
def jr(rs): return (RN[rs] << 21) | 0x08
def addu(rd, rs, rt): return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x21
def or_(rd, rs, rt): return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x25
def daddu(rd, rs, rt): return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x2D
NOP = 0


if __name__ == "__main__":
    if sys.argv[1] == "dis":
        e = Elf(sys.argv[2])
        a, b = int(sys.argv[3], 16), int(sys.argv[4], 16)
        for pc in range(a, b, 4):
            w = e.word(pc)
            print(f"{pc:08X}  {w:08X}  {dis(w, pc)}")
