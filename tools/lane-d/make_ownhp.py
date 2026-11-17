"""Lane D: 'each hero has its own HP and MP' patch.

  python -I tools/lane-d/make_ownhp.py <outDir> [v1|v2]

Base = lane A's controller patch (patches/lane-a-p2pad-v3), copied unchanged.

Background (VERIFIED, docs/lanes/D-own-hp.md). A character's HP/MP/stats live in a "unit slot" (0x268 bytes, pool
of 64 at 0x01C62FB8, handed out from the top, so the first one is 0x01C6C750). A player object gets its slot in
the player base constructor (0x00177DC8): at 0x00177E74 it calls 0x001A15D0(statusId, formArg), which looks for
an existing slot with the same status id (1 = Sora, 14 = Roxas) and re-uses it. That is why a twin shares HP.
The game also has 0x001A1728(statusId, formArg): "always make a fresh slot for this id".

v1  D1 (hook 0x00177E74): if a player object already exists (0x00352400 != 0, the same test lane A uses for
       "this is the second hero"), call 0x001A1728 instead and mark the new slot (bit 31 of slot+0x250).
    D2 (hook 0x001A1518, inside the find-by-id loop of 0x001A1490): a marked slot is never returned by a search,
       so every "Sora's slot" lookup in the game still gets player 1's slot.
v2  v1 + the twin's slot keeps its own copy of the save-side character record, so that the twin's HP/MP are not
    written into (or read from) player 1's record:
    D3 (called from D1): slot+0x244 = private record T; T is refreshed from player 1's record except the
       current-HP and current-MP bytes (first time or HP 0: everything is copied).
    D4 (hook 0x001A1208, start of the slot's "load stats from the record" routine 0x001A11E0): the same refresh
       every time the twin slot reloads its stats, so equipment / level changes reach the twin.
Code cave: 0x000F0100-0x000F02FF (lane D's range). Private record T: 0x000F01E0, 0x114 bytes.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-a"))
from mips import RN, jal, j, lui, lw, sw, sd, ld, lbu, addiu, ori, jr, beq, bne, daddu, NOP  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent.parent / "patches" / "lane-a-p2pad-v3" / "SLPM-66675_F266B00B.pnach"

FIND_OR_SHARE = 0x001A15D0   # (statusId, formArg) -> slot, re-uses a slot with the same id
FRESH_SLOT = 0x001A1728      # (statusId, formArg) -> a new slot for that id
CHAR_RECORD = 0x00188FE0     # (0x0032E020, statusId) -> the character's record inside the save data
LAST_PLAYER = 0x00352400     # pointer to the last built player object, 0 if none
D1 = 0x000F0100
D2 = 0x000F0150
D3 = 0x000F0170
D4 = 0x000F01B0
T = 0x000F01E0               # private character record of the twin (0x114 bytes, ends 0x000F02F3)
REC = 0x114


def _i(op, rs, rt, imm):
    return (op << 26) | (RN[rs] << 21) | (RN[rt] << 16) | (imm & 0xFFFF)


def bltz(rs, pc, target):
    return (1 << 26) | (RN[rs] << 21) | (((target - (pc + 4)) >> 2) & 0xFFFF)


def or_(rd, rs, rt):
    return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x25


def sb(rt, off, rs):
    return _i(0x28, rs, rt, off)


def sltu(rd, rs, rt):
    return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x2B


class Asm:
    def __init__(self, base):
        self.base, self.words, self.labels, self.fix = base, [], {}, []

    @property
    def pc(self):
        return self.base + 4 * len(self.words)

    def label(self, name):
        self.labels[name] = self.pc

    def emit(self, w):
        self.words.append(w)

    def br(self, kind, rs, rt, name):
        self.fix.append((len(self.words), kind, rs, rt, name))
        self.words.append(0)

    def done(self):
        for idx, kind, rs, rt, name in self.fix:
            pc, tgt = self.base + 4 * idx, self.labels[name]
            self.words[idx] = {"beq": lambda: beq(rs, rt, pc, tgt), "bne": lambda: bne(rs, rt, pc, tgt),
                               "bltz": lambda: bltz(rs, pc, tgt)}[kind]()
        return {self.base + 4 * i: w for i, w in enumerate(self.words)}


def build(variant):
    code = {}
    # ---- D1: called instead of 0x001A15D0 from the player base constructor (a0 = status id, a1 = form arg) ----
    a = Asm(D1)
    a.emit(lui("t7", LAST_PLAYER >> 16))
    a.emit(lw("t7", LAST_PLAYER & 0xFFFF, "t7"))
    a.br("bne", "t7", "zero", "twin")
    a.emit(NOP)
    a.emit(j(FIND_OR_SHARE))                 # first hero: unchanged behaviour
    a.emit(NOP)
    a.label("twin")
    a.emit(addiu("sp", "sp", -16))
    a.emit(sd("ra", 0, "sp"))
    a.emit(jal(FRESH_SLOT))                  # second hero: a slot of its own
    a.emit(NOP)
    a.br("beq", "v0", "zero", "out")
    a.emit(lui("t6", 0x8000))
    a.emit(lw("t7", 0x250, "v0"))
    a.emit(or_("t7", "t7", "t6"))
    a.emit(sw("t7", 0x250, "v0"))            # mark: this is the second hero's slot
    if variant == "v2":
        a.emit(jal(D3))                      # give it a private record and reload the stats from it
        a.emit(daddu("a0", "v0", "zero"))
    a.label("out")
    a.emit(ld("ra", 0, "sp"))
    a.emit(jr("ra"))
    a.emit(addiu("sp", "sp", 16))
    assert a.pc <= D2, hex(a.pc)
    code.update(a.done())

    # ---- D2: inside the find-by-id loop (s0 = slot, s1 = wanted id, t7 = slot id, a1 = s0 already) ----
    a = Asm(D2)
    a.br("bne", "t7", "s1", "next")
    a.emit(lw("t6", 0x250, "s0"))
    a.br("bltz", "t6", None, "next")         # marked slot: keep searching
    a.emit(NOP)
    a.emit(j(0x001A1520))                    # found (original continuation)
    a.emit(NOP)
    a.label("next")
    a.emit(j(0x001A14C4))                    # original loop head
    a.emit(NOP)
    assert a.pc <= D3, hex(a.pc)
    code.update(a.done())

    patches = {
        0x00177E74: jal(D1),                 # was: jal 0x001A15D0
        0x001A1518: j(D2),                   # was: bne t7,s1,0x001A14C4 (its delay slot 'move a1,s0' stays)
    }

    if variant == "v2":
        # ---- D3(a0 = twin slot): slot->record = T, refresh T, reload stats; returns the slot in v0 ----
        a = Asm(D3)
        a.emit(addiu("sp", "sp", -32))
        a.emit(sd("ra", 0, "sp"))
        a.emit(sd("s0", 8, "sp"))
        a.emit(daddu("s0", "a0", "zero"))
        a.emit(lui("t7", T >> 16))
        a.emit(ori("t7", "t7", T & 0xFFFF))
        a.emit(sw("t7", 0x244, "s0"))        # slot->record = T
        a.emit(daddu("a0", "s0", "zero"))
        a.emit(jal(0x001A11E0))              # load stats from the record (D4 refreshes T first)
        a.emit(daddu("a1", "zero", "zero"))
        a.emit(daddu("v0", "s0", "zero"))
        a.emit(ld("ra", 0, "sp"))
        a.emit(ld("s0", 8, "sp"))
        a.emit(jr("ra"))
        a.emit(addiu("sp", "sp", 32))
        assert a.pc <= D4, hex(a.pc)
        code.update(a.done())
        # ---- D4: start of 0x001A11E0 when called with record == 0 (a0 = s0 = slot); returns to 0x001A1208 ----
        # original at 0x001A1208: lw a1,0x244(a0) ; 0x001A120C: beq a1,zero,exit ; 0x001A1210: _move s1,a1
        # We replace 0x001A1208 with 'j D4' is not possible without losing an instruction slot, so the hook
        # replaces the pair 0x001A1200/04 instead (bne a1,zero,+ ; _move s1,a1) -- see patches below.
        raise SystemExit("v2 is built by make_ownhp2.py")

    return code, patches


def main():
    out = pathlib.Path(sys.argv[1])
    variant = sys.argv[2] if len(sys.argv) > 2 else "v1"
    code, patches = build(variant)
    base = [l for l in BASE.read_text().splitlines() if l.startswith("patch=")]
    if "nobase" in sys.argv:
        base = []   # experiments only: both heroes stay on controller 1
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        f"comment=Two-player project, lane D {variant} (own HP/MP slot for the second hero) on top of lane A v3 (pad).",
        "comment=Every PC in an online game must have this same file (it changes game code).",
    ] + base
    for addr in sorted(code):
        lines.append(f"patch=1,EE,{addr:08X},word,{code[addr]:08X}")
    for addr in sorted(patches):
        lines.append(f"patch=1,EE,{addr:08X},word,{patches[addr]:08X}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    print(f"wrote {out / 'SLPM-66675_F266B00B.pnach'}: {len(base)} base lines + {len(code)} code words + {len(patches)} hooks")


if __name__ == "__main__":
    main()
