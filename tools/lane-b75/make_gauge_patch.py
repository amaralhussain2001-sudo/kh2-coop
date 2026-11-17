"""Lane B75: write the patch lines that let the enemy HP gauge show a boss with more than 3400 HP.

  python -I tools/lane-b75/make_gauge_patch.py <out.txt> [--elf local/iso-files/SLPM_666.75]

WHY (VERIFIED, see docs/lanes/B75-boss-hp.md): the gauge has 16 small bars + 1 long bar, 200 HP each = 3400 HP.
The routines that set the gauge loop over (HP - 1) / 200 small bars without a bound (0x00154B98, 0x00154C10),
so HP above 3400 walks past the 16th bar and the game freezes. The original game never has more than 3400.

WHAT: three small detours into the lane's code cave (0x000F3800..). The real maximum of the current gauge is
kept in one word (0x000F3FF0). If it is above 3400, the gauge is given maximum 3400 and every HP value is shown
in proportion:  shown = ceil(HP * 3400 / real maximum).  For a maximum of 3400 or less nothing changes at all
(except that an HP value above 3400 handed to the gauge is shown as 3400 instead of freezing the game).
Only the picture changes; the real HP in the unit slot is never touched, so both PCs stay identical.

  0x00154450  gauge start (a0 gauge, a1 HP, a2 maximum)   -> keep the real maximum, give the gauge min(maximum, 3400)
  0x00154B98  gauge set   (a0 gauge, a1 HP)               -> scale a1
  0x00154C10  gauge update after damage (a0 gauge, a1 HP) -> scale a1
"""
import struct
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 2)[0] + "/lane-a")
import mips  # noqa: E402

LIMIT = 3400
CAVE = 0x000F3800
VAR = 0x000F3FF0
R = mips.RN


def spec(funct, rs="zero", rt="zero", rd="zero"):
    return (R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | funct


def slti(rt, rs, imm):
    return (0x0A << 26) | (R[rs] << 21) | (R[rt] << 16) | (imm & 0xFFFF)


def blez(rs, pc, target):
    return (0x06 << 26) | (R[rs] << 21) | (((target - (pc + 4)) >> 2) & 0xFFFF)


NOP = 0


def scale_block(pc):
    """a1 = ceil(a1 * LIMIT / real maximum) when the real maximum is above LIMIT and a1 > 0; then a1 = min(a1, LIMIT).
    Uses t5, t6, t7, HI/LO."""
    out = pc + 4 * 13
    return [
        mips.lui("t7", VAR >> 16),
        mips.lw("t7", VAR & 0xFFFF, "t7"),          # real maximum
        slti("t6", "t7", LIMIT + 1),
        mips.bne("t6", "zero", pc + 12, out),       # maximum fits: leave a1 alone
        NOP,
        blez("a1", pc + 20, out),
        mips.addiu("t5", "zero", LIMIT),            # (delay slot)
        spec(0x18, "a1", "t5"),                     # mult a1,t5
        spec(0x12, rd="t6"),                        # mflo t6
        mips.addu("t6", "t6", "t7"),
        mips.addiu("t6", "t6", -1),                 # round up, so a living boss never shows an empty gauge
        spec(0x1A, "t6", "t7"),                     # div t6,t7
        spec(0x12, rd="a1"),                        # mflo a1
        # out: whatever the value, never hand the gauge more than LIMIT (it has no bound of its own)
        slti("t6", "a1", LIMIT + 1),
        mips.addiu("t5", "zero", LIMIT),
        spec(0x0A, "t5", "t6", "a1"),               # movz a1,t5,t6
    ]


def build():
    words = {}
    pc = CAVE
    # --- gauge start
    init = pc
    code = [
        mips.lui("t7", VAR >> 16),
        mips.sw("a2", VAR & 0xFFFF, "t7"),          # remember the real maximum
        slti("t6", "a2", LIMIT + 1),
        mips.bne("t6", "zero", pc + 12, pc + 24),
        NOP,
        mips.addiu("a2", "zero", LIMIT),
        mips.j(0x00154458),
        mips.sw("a2", 15556, "a0"),                 # original instruction of 0x00154454 (delay slot)
    ]
    for w in code:
        words[pc] = w
        pc += 4
    # --- gauge set
    setp = pc
    code = scale_block(pc) + [mips.j(0x00154BA0), mips.addiu("t4", "zero", 200)]   # original 0x00154B9C
    for w in code:
        words[pc] = w
        pc += 4
    # --- gauge update
    upd = pc
    code = scale_block(pc) + [mips.j(0x00154C18), slti("t7", "a1", 0)]             # original 0x00154C14
    for w in code:
        words[pc] = w
        pc += 4
    end = pc
    hooks = {
        0x00154450: mips.j(init), 0x00154454: mips.addiu("sp", "sp", -32),
        0x00154B98: mips.j(setp), 0x00154B9C: mips.addiu("sp", "sp", -32),
        0x00154C10: mips.j(upd), 0x00154C14: mips.addiu("sp", "sp", -64),
    }
    return words, hooks, (init, setp, upd, end)


EXPECT = {0x00154450: 0x27BDFFE0, 0x00154454: 0xAC863CC4, 0x00154B98: 0x27BDFFE0, 0x00154B9C: 0x240C00C8,
          0x00154C10: 0x27BDFFC0, 0x00154C14: 0x28AF0000}


def main():
    out = sys.argv[1]
    elf = sys.argv[sys.argv.index("--elf") + 1] if "--elf" in sys.argv else None
    words, hooks, (init, setp, upd, end) = build()
    if elf:
        e = mips.Elf(elf)
        va, off, fs = e.segs[0]
        for a, want in EXPECT.items():
            got = struct.unpack_from("<I", e.data, off + (a - va))[0]
            assert got == want, "the game program differs at 0x%08X: %08X, expected %08X" % (a, got, want)
        print("game program checked: the six replaced instructions are the expected ones")
    assert end <= VAR
    lines = ["comment=LANE B75 HP gauge: bosses above 3400 HP are shown in proportion (cave 0x%08X-0x%08X, word 0x%08X)"
             % (CAVE, end - 4, VAR)]
    for a in sorted(words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, words[a]))
    for a in sorted(hooks):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hooks[a]))
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("lines:", len(lines) - 1, "| cave 0x%08X..0x%08X | start 0x%08X set 0x%08X update 0x%08X" % (CAVE, end - 4, init, setp, upd))
    for a in sorted(words):
        print("  %08X  %08X  %s" % (a, words[a], mips.dis(words[a], a)))
    for a in sorted(hooks):
        print("  %08X  %08X  %s   (was %08X)" % (a, hooks[a], mips.dis(hooks[a], a), EXPECT[a]))


if __name__ == "__main__":
    main()
