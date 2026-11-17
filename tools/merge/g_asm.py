"""Lane G: a very small label-aware MIPS assembler for patch routines (only the instructions we need).

    a = Asm(0x000F0800)
    a.label("start"); a.lui("t7", 0x35); a.beq("t6", "zero", "done"); a.nop(); ...
    words = a.build()          # {address: word}
"""
R = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
     "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]
RN = {n: i for i, n in enumerate(R)}


class Asm:
    def __init__(self, base, limit=None):
        self.base, self.limit = base, limit
        self.items = []          # callables (pc, labels) -> word
        self.labels = {}
        self.notes = {}          # address -> comment

    @property
    def pc(self):
        return self.base + 4 * len(self.items)

    def label(self, name):
        if name in self.labels:
            raise ValueError("duplicate label " + name)
        self.labels[name] = self.pc

    def _emit(self, fn, note=""):
        self.notes[self.pc] = note
        self.items.append(fn)

    def _i(self, op, rs, rt, imm, note=""):
        if not -0x8000 <= imm <= 0xFFFF:
            raise ValueError("immediate out of range: %r" % imm)
        w = (op << 26) | (RN[rs] << 21) | (RN[rt] << 16) | (imm & 0xFFFF)
        self._emit(lambda pc, lb: w, note)

    def _r(self, rs, rt, rd, fn, note=""):
        w = (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | fn
        self._emit(lambda pc, lb: w, note)

    def nop(self, note=""): self._emit(lambda pc, lb: 0, note)
    def lui(self, rt, imm, note=""): self._i(0x0F, "zero", rt, imm, note)
    def ori(self, rt, rs, imm, note=""): self._i(0x0D, rs, rt, imm, note)
    def andi(self, rt, rs, imm, note=""): self._i(0x0C, rs, rt, imm, note)
    def addiu(self, rt, rs, imm, note=""): self._i(0x09, rs, rt, imm, note)
    def lw(self, rt, off, rs, note=""): self._i(0x23, rs, rt, off, note)
    def sw(self, rt, off, rs, note=""): self._i(0x2B, rs, rt, off, note)
    def lbu(self, rt, off, rs, note=""): self._i(0x24, rs, rt, off, note)
    def sb(self, rt, off, rs, note=""): self._i(0x28, rs, rt, off, note)
    def lhu(self, rt, off, rs, note=""): self._i(0x25, rs, rt, off, note)
    def sh(self, rt, off, rs, note=""): self._i(0x29, rs, rt, off, note)
    def ld(self, rt, off, rs, note=""): self._i(0x37, rs, rt, off, note)
    def sd(self, rt, off, rs, note=""): self._i(0x3F, rs, rt, off, note)
    def lq(self, rt, off, rs, note=""): self._i(0x1E, rs, rt, off, note)
    def sq(self, rt, off, rs, note=""): self._i(0x1F, rs, rt, off, note)
    def daddu(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x2D, note)
    def addu(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x21, note)
    def subu(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x23, note)
    def or_(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x25, note)
    def and_(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x24, note)
    def sltu(self, rd, rs, rt, note=""): self._r(rs, rt, rd, 0x2B, note)
    def jr(self, rs, note=""): self._emit(lambda pc, lb, w=(RN[rs] << 21) | 0x08: w, note)

    def _target(self, t, lb):
        return lb[t] if isinstance(t, str) else t

    def j(self, target, note=""):
        self._emit(lambda pc, lb: (0x02 << 26) | ((self._target(target, lb) >> 2) & 0x3FFFFFF), note)

    def jal(self, target, note=""):
        self._emit(lambda pc, lb: (0x03 << 26) | ((self._target(target, lb) >> 2) & 0x3FFFFFF), note)

    def _br(self, op, rs, rt, target, note):
        def fn(pc, lb):
            off = (self._target(target, lb) - (pc + 4)) >> 2
            if not -0x8000 <= off < 0x8000:
                raise ValueError("branch too far")
            return (op << 26) | (RN[rs] << 21) | (RN[rt] << 16) | (off & 0xFFFF)
        self._emit(fn, note)

    def beq(self, rs, rt, target, note=""): self._br(0x04, rs, rt, target, note)
    def bne(self, rs, rt, target, note=""): self._br(0x05, rs, rt, target, note)

    def li32(self, rt, value, note=""):
        """load a 32-bit constant (lui + ori)"""
        self.lui(rt, (value >> 16) & 0xFFFF, note)
        self.ori(rt, rt, value & 0xFFFF)

    def build(self):
        out = {}
        for i, fn in enumerate(self.items):
            pc = self.base + 4 * i
            out[pc] = fn(pc, self.labels) & 0xFFFFFFFF
        if self.limit is not None and self.pc > self.limit:
            raise ValueError("routine area overflow: ends at 0x%08X, limit 0x%08X" % (self.pc, self.limit))
        return out


def j_word(target):
    return (0x02 << 26) | ((target >> 2) & 0x3FFFFFF)


def jal_word(target):
    return (0x03 << 26) | ((target >> 2) & 0x3FFFFFF)
