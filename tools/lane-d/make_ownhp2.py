"""Lane D: 'each hero has its own HP and MP' patch, version 2 (the delivered one).

  python -I tools/lane-d/make_ownhp2.py <outDir> [nobase] [nosib]

Base = lane A's controller patch (patches/lane-a-p2pad-v3), copied unchanged ('nobase' leaves it out: both
heroes then stay on controller 1; experiments only). 'nosib' leaves out routine D6 (experiments only).

What it does (CRC F266B00B; details and evidence in docs/lanes/D-own-hp.md):
 D1  hook 0x00177E74 (player base constructor asks for its unit slot): if a player object already exists
     (0x00352400 != 0, lane A's test for "this is the second hero") the object gets a FRESH slot from the game's
     own routine 0x001A1728 instead of sharing the one with the same status id; the slot is marked
     (bit 31 of slot+0x250) and its stats are loaded once more so that R/RM below apply.
 D2  hook 0x001A1518 (find-slot-by-id loop of 0x001A1490): a marked slot is never returned by a search, so every
     "Sora's slot" lookup in the game still gets player 1's slot.
 R   hook 0x001A1238, RM hook 0x001A1248 (slot loads current HP / MP from the character record): a marked slot
     takes them from two bytes of its own in the save data instead (0 = none stored: use the record's).
 W1  hook 0x001A1854, W2 hook 0x001A1870 (slot writes current HP / MP back into the record): a marked slot
     writes them to those two bytes instead, so it never changes player 1's saved HP/MP.
 D6  hook 0x001A1438 (end of 'load slot stats from record' 0x001A11E0): when a hero slot (status id 1 or 14) was
     reloaded, every other slot with the same id is written back and reloaded too, so level-ups, equipment and
     ability changes reach both heroes at the same moment.
The second hero keeps using player 1's character record for everything except current HP and MP, so max HP/MP,
strength, defence, abilities and level are always equal.
Second hero's own bytes: save data + 0x1E5E (HP) and + 0x1E5F (MP + 1) = 0x0032D98E / 0x0032D98F.
Code cave 0x000F0100-0x000F02EF, one work flag at 0x000F02F0 (lane D's range is 0x000F0100-0x000F02FF).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-a"))
from mips import RN, dis  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "patches" / "lane-a-p2pad-v3" / "SLPM-66675_F266B00B.pnach"

FIND_OR_SHARE = 0x001A15D0
FRESH_SLOT = 0x001A1728
LOAD_STATS = 0x001A11E0
WRITE_BACK = 0x001A1840
NEXT_USED = 0x0031F168
ABIL_END = 0x001C3060
LAST_PLAYER = 0x00352400
POOL = 0x01C62FB8
SAVE_HP = 0x0032D98E          # save data + 0x1E5E
SAVE_MP = 0x0032D98F          # save data + 0x1E5F (stored as MP + 1)
CAVE = 0x000F0100
BUSY = 0x000F02F0


def hi(a):
    return ((a + 0x8000) >> 16) & 0xFFFF


def lo(a):
    return a & 0xFFFF


class Asm:
    """Tiny label-aware assembler for the handful of instructions used here."""

    def __init__(self, base):
        self.base, self.items, self.labels = base, [], {}

    @property
    def pc(self):
        return self.base + 4 * len(self.items)

    def L(self, name):
        self.labels[name] = self.pc

    def _i(self, op, rs, rt, imm):
        self.items.append((op << 26) | (RN[rs] << 21) | (RN[rt] << 16) | (imm & 0xFFFF))

    def _r(self, fn, rd, rs, rt):
        self.items.append((RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | fn)

    def lui(self, rt, imm): self._i(0x0F, "zero", rt, imm)
    def addiu(self, rt, rs, imm): self._i(0x09, rs, rt, imm)
    def lw(self, rt, off, rs): self._i(0x23, rs, rt, off)
    def sw(self, rt, off, rs): self._i(0x2B, rs, rt, off)
    def lbu(self, rt, off, rs): self._i(0x24, rs, rt, off)
    def sb(self, rt, off, rs): self._i(0x28, rs, rt, off)
    def ld(self, rt, off, rs): self._i(0x37, rs, rt, off)
    def sd(self, rt, off, rs): self._i(0x3F, rs, rt, off)
    def or_(self, rd, rs, rt): self._r(0x25, rd, rs, rt)
    def move(self, rd, rs): self._r(0x2D, rd, rs, "zero")       # daddu rd,rs,zero
    def slt(self, rd, rs, rt): self._r(0x2A, rd, rs, rt)
    def movn(self, rd, rs, rt): self._r(0x0B, rd, rs, rt)       # rd = rs if rt != 0
    def movz(self, rd, rs, rt): self._r(0x0A, rd, rs, rt)       # rd = rs if rt == 0
    def nop(self): self.items.append(0)
    def jr(self, rs): self.items.append((RN[rs] << 21) | 0x08)
    def j(self, target): self.items.append((0x02 << 26) | ((target >> 2) & 0x3FFFFFF))
    def jal(self, target): self.items.append((0x03 << 26) | ((target >> 2) & 0x3FFFFFF))
    def beq(self, rs, rt, label): self.items.append(("b", 0x04, rs, rt, label))
    def bne(self, rs, rt, label): self.items.append(("b", 0x05, rs, rt, label))
    def bltz(self, rs, label): self.items.append(("r", 0x00, rs, None, label))
    def bgez(self, rs, label): self.items.append(("r", 0x01, rs, None, label))

    def words(self):
        out = {}
        for idx, it in enumerate(self.items):
            pc = self.base + 4 * idx
            if isinstance(it, tuple):
                kind, code, rs, rt, label = it
                off = ((self.labels[label] - (pc + 4)) >> 2) & 0xFFFF
                if kind == "b":
                    it = (code << 26) | (RN[rs] << 21) | (RN[rt] << 16) | off
                else:
                    it = (1 << 26) | (RN[rs] << 21) | (code << 16) | off
            out[pc] = it
        return out


def build(sibling=True):
    a = Asm(CAVE)
    hooks = {}

    # ---- D1: called instead of 0x001A15D0 from the player base constructor (a0 = status id, a1 = form arg) ----
    a.L("D1")
    a.lui("t7", hi(LAST_PLAYER)); a.lw("t7", lo(LAST_PLAYER), "t7")
    a.bne("t7", "zero", "D1_second"); a.nop()
    a.j(FIND_OR_SHARE); a.nop()                       # first hero: unchanged behaviour
    a.L("D1_second")
    a.addiu("sp", "sp", -16); a.sd("ra", 0, "sp")
    a.jal(FRESH_SLOT); a.nop()                        # second hero: a slot of its own
    a.beq("v0", "zero", "D1_out"); a.lui("t6", 0x8000)
    a.lw("t7", 0x250, "v0"); a.or_("t7", "t7", "t6"); a.sw("t7", 0x250, "v0")   # mark it
    a.sd("v0", 8, "sp")
    a.move("a0", "v0")
    a.jal(LOAD_STATS); a.move("a1", "zero")           # load once more, now as a marked slot
    a.ld("v0", 8, "sp")
    a.L("D1_out")
    a.ld("ra", 0, "sp"); a.jr("ra"); a.addiu("sp", "sp", 16)
    hooks[0x00177E74] = ("jal", "D1")                 # was: jal 0x001A15D0

    # ---- D2: find-by-id loop (s0 = slot, s1 = wanted id, t7 = slot id; 'move a1,s0' already done) ----
    a.L("D2")
    a.bne("t7", "s1", "D2_next"); a.lw("t6", 0x250, "s0")
    a.bltz("t6", "D2_next"); a.nop()                  # marked slot: keep searching
    a.j(0x001A1520); a.nop()                          # found
    a.L("D2_next")
    a.j(0x001A14C4); a.nop()                          # loop head
    hooks[0x001A1518] = ("j", "D2")                   # was: bne t7,s1,0x001A14C4

    # ---- R: current HP for the slot being loaded (s0 = slot, s1 = record, t5 = max HP) ----
    a.L("R")
    a.lbu("t7", 4, "s1")                              # the record's current HP (the original instruction)
    a.lw("t6", 0x250, "s0")
    a.bgez("t6", "R_done"); a.lui("t6", hi(SAVE_HP))
    a.lbu("t6", lo(SAVE_HP), "t6")                    # second hero's own saved HP (0 = none)
    a.movn("t7", "t6", "t6")
    a.L("R_done")
    a.jr("ra"); a.slt("t6", "t5", "t7")               # redo the compare that sat in the delay slot
    hooks[0x001A1238] = ("jal", "R")                  # was: lbu t7,4(s1)

    # ---- RM: current MP (s0 = slot, s1 = record) ----
    a.L("RM")
    a.lbu("t6", 6, "s1")                              # the record's current MP (the original instruction)
    a.lw("t7", 0x250, "s0")
    a.bgez("t7", "RM_done"); a.lui("t7", hi(SAVE_MP))
    a.lbu("t7", lo(SAVE_MP), "t7")                    # second hero's own saved MP + 1 (0 = none)
    a.beq("t7", "zero", "RM_done"); a.nop()
    a.addiu("t6", "t7", -1)
    a.L("RM_done")
    a.jr("ra"); a.nop()
    hooks[0x001A1248] = ("jal", "RM")                 # was: lbu t6,6(s1)

    # ---- W1: write current HP back (a0 = slot, t6 = record, t7 = HP byte) ----
    a.L("W1")
    a.lw("t5", 0x250, "a0")
    a.bltz("t5", "W1_second"); a.nop()
    a.j(0x001A185C); a.sb("t7", 4, "t6")              # normal slot: into its record (the original instruction)
    a.L("W1_second")
    a.lui("t5", hi(SAVE_HP))
    a.j(0x001A185C); a.sb("t7", lo(SAVE_HP), "t5")    # second hero: into its own save byte
    hooks[0x001A1854] = ("j", "W1")                   # was: sb t7,4(t6)

    # ---- W2: write current MP back (a0 = slot, t5 = record, t7 = MP byte) ----
    a.L("W2")
    a.lw("t4", 0x250, "a0")
    a.bltz("t4", "W2_second"); a.nop()
    a.j(0x001A1878); a.sb("t7", 6, "t5")              # normal slot (the original instruction)
    a.L("W2_second")
    a.lui("t4", hi(SAVE_HP))
    a.lbu("t3", lo(SAVE_HP), "t4")                    # the HP just stored
    a.addiu("t7", "t7", 1)
    a.movz("t7", "zero", "t3")                        # HP 0: store "none", the hero restarts from player 1's values
    a.j(0x001A1878); a.sb("t7", lo(SAVE_MP), "t4")
    hooks[0x001A1870] = ("j", "W2")                   # was: sb t7,6(t5)

    if sibling:
        # ---- D6: end of 0x001A11E0 (a0 = slot + 0x1CC, frame already released, ra = caller) ----
        a.L("D6")
        a.addiu("sp", "sp", -32); a.sd("ra", 0, "sp"); a.sd("s0", 8, "sp"); a.sd("s1", 16, "sp")
        a.addiu("s0", "a0", -0x1CC)
        a.jal(ABIL_END); a.nop()                      # the original tail call
        a.lui("t7", hi(BUSY)); a.lw("t6", lo(BUSY), "t7")
        a.bne("t6", "zero", "D6_out"); a.lw("t5", 0x254, "s0")
        a.addiu("t6", "zero", 1)
        a.beq("t5", "t6", "D6_hero"); a.addiu("t6", "zero", 14)
        a.bne("t5", "t6", "D6_out"); a.nop()
        a.L("D6_hero")
        a.sw("t6", lo(BUSY), "t7")                    # busy (non-zero)
        a.move("s1", "zero")
        a.L("D6_loop")
        a.lui("a0", hi(POOL)); a.addiu("a0", "a0", lo(POOL))
        a.jal(NEXT_USED); a.move("a1", "s1")          # next slot in use
        a.beq("v0", "zero", "D6_end"); a.move("s1", "v0")
        a.beq("s1", "s0", "D6_loop"); a.lw("t6", 0x254, "s1")
        a.lw("t5", 0x254, "s0")
        a.bne("t6", "t5", "D6_loop"); a.nop()
        a.jal(WRITE_BACK); a.move("a0", "s1")         # the other hero: save its current HP/MP ...
        a.move("a0", "s1")
        a.jal(LOAD_STATS); a.move("a1", "zero")       # ... and reload its stats from the shared record
        a.beq("zero", "zero", "D6_loop"); a.nop()
        a.L("D6_end")
        a.lui("t7", hi(BUSY)); a.sw("zero", lo(BUSY), "t7")
        a.L("D6_out")
        a.ld("ra", 0, "sp"); a.ld("s0", 8, "sp"); a.ld("s1", 16, "sp")
        a.jr("ra"); a.addiu("sp", "sp", 32)
        hooks[0x001A1438] = ("j", "D6")               # was: j 0x001C3060

    assert a.pc <= BUSY, hex(a.pc)
    code = a.words()
    patches = {}
    for addr, (kind, label) in hooks.items():
        t = a.labels[label]
        patches[addr] = ((0x03 if kind == "jal" else 0x02) << 26) | ((t >> 2) & 0x3FFFFFF)
    return code, patches, a.labels, a.pc


def main():
    out = pathlib.Path(sys.argv[1])
    code, patches, labels, end = build(sibling="nosib" not in sys.argv)
    base = [l for l in BASE.read_text().splitlines() if l.startswith("patch=")]
    if "nobase" in sys.argv:
        base = []
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, lane D v2 (own HP/MP for the second hero) on top of lane A v3 (pad).",
        "comment=Every PC in an online game must have this same file (it changes game code).",
    ] + base
    for addr in sorted(code):
        lines.append(f"patch=1,EE,{addr:08X},word,{code[addr]:08X}")
    for addr in sorted(patches):
        lines.append(f"patch=1,EE,{addr:08X},word,{patches[addr]:08X}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    listing = []
    names = {v: k for k, v in labels.items()}
    for addr in sorted(code):
        if addr in names:
            listing.append(f"{names[addr]}:")
        listing.append(f"  {addr:08X}  {code[addr]:08X}  {dis(code[addr], addr)}")
    for addr in sorted(patches):
        listing.append(f"hook {addr:08X}  {patches[addr]:08X}  {dis(patches[addr], addr)}")
    (out / "listing.txt").write_text("\n".join(listing) + "\n")
    print(f"wrote {out}: {len(base)} base lines, {len(code)} code words (cave ends 0x{end:08X}), {len(patches)} hooks")


if __name__ == "__main__":
    main()
