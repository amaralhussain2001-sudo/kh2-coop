"""Lane A: 'each player object uses its own controller' patch, version 4 (= version 3 + player 1 stays the
game's main player).

  python -I tools/lane-a/make_p2pad4.py <outDir> [pad|padplayer] [keep1|keep2|keep2cam|keep2slot|keep2s]

Background (VERIFIED, see docs/lanes/A-pad-path.md): player objects take normal movement and jump input from ONE
shared control object S (0x01C5F530). Each player object's update calls S's update, which copies stick and button
flags from S->pad (S+0x9E4). The game also keeps "the player" pointers that the LAST built player object
overwrites (0x00352400 and 0x0034E948), so with a second player object the camera follows the second one.

Patch (CRC F266B00B, Kingdom Hearts II Final Mix, SLPM-66675):
 A. Player factory 0x0017A000: first player object -> logical controller 0, any further one -> 1.
    The pointers 0x00352400 / 0x0034E948 seen before building are remembered at 0x000F0100 / 0x000F0104.
 B. Player method 0x00178888: just before S's update, S->pad = this object's controller (object+0xB38);
    variant 'padplayer' also sets S->player (S+0x9E0) = this object.
 C. Player constructor call 0x0017A054 (keep1 = 0x00352400 only, keep2 = both pointers): after a FURTHER player
    object is built, the remembered pointer(s) are written back, so the first object stays "the player".
Code lives in unused memory from 0x000F0000 (zero in every memory dump checked).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mips import RN, addiu, beq, jal, j, jr, ld, lui, lw, sd, sw, daddu, NOP  # noqa: E402

GETTER = 0x00167F18
PLAYER_CTOR = 0x001D0980
S_UPDATE_WRAPPER = 0x001D6BA0
CAVE_A, CAVE_B, CAVE_C = 0x000F0000, 0x000F0040, 0x000F0060
SCR = 0x0100   # scratch words at 0x000F0100 (saved 0x00352400) and 0x000F0104 (saved 0x0034E948)


def sltu(rd, rs, rt):
    return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x2B


def main():
    out = pathlib.Path(sys.argv[1])
    variant = sys.argv[2] if len(sys.argv) > 2 else "pad"
    keep = sys.argv[3] if len(sys.argv) > 3 else "keep2"
    a = [
        lui("t7", 0x0035),
        lw("t6", 0x2400, "t7"),            # pointer to the last built player object (0 if none)
        lui("t5", 0x000F),
        sw("t6", SCR, "t5"),               # remember it
        lw("t4", -0x16B8, "t7"),           # 0x0034E948 (0x00350000 - 0x16B8)
        sw("t4", SCR + 4, "t5"),           # remember it
        j(GETTER),
        sltu("a0", "zero", "t6"),          # controller index = 1 if a player object already exists
    ]
    b = [lw("t6", 0xB38, "a0")]            # a0 = this object, t7 = S
    if variant == "padplayer":
        b.append(sw("a0", 0x9E0, "t7"))
    b += [sw("t6", 0x9E4, "t7"), j(S_UPDATE_WRAPPER), daddu("a0", "t7", "zero")]
    c = [
        addiu("sp", "sp", -16),
        sd("ra", 0, "sp"),
        jal(PLAYER_CTOR),
        NOP,
        lui("t5", 0x000F),
        lw("t6", SCR, "t5"),               # the player that existed before this one was built
        0,                                 # placeholder for the branch (filled below)
        lui("t7", 0x0035),                 # delay slot
        sw("t6", 0x2400, "t7"),            # 0x00352400 = first player again
    ]
    if keep in ("keep2", "keep2cam", "keep2slot", "keep2s"):
        c += [lw("t4", SCR + 4, "t5"), sw("t4", -0x16B8, "t7")]   # 0x0034E948 = its old value
    if keep == "keep2slot":
        # the unit slot (object+0x48C) keeps a back pointer to its object at slot+0x25C; both player objects
        # share slot 1, so the second object overwrote it. Point it back at the first object.
        c += [lw("t3", 0x48C, "t6"), sw("t6", 0x25C, "t3")]
    if keep == "keep2s":
        # the shared control object S remembers the last attached player at S+0x9E0 (0x01C5FF10) and
        # S+0xAF4 (0x01C60024); point both back at the first player object.
        c += [lui("t3", 0x01C6), sw("t6", -0xF0, "t3"), sw("t6", 0x24, "t3")]
    if keep == "keep2cam":
        # camera: the attach routine pointed the camera at the new object (FUN_0013ddc0(0, object));
        # point it back at the first player object.
        c += [daddu("a1", "t6", "zero"), jal(0x0013DDC0), daddu("a0", "zero", "zero")]
    skip_index = len(c)
    c += [ld("ra", 0, "sp"), jr("ra"), addiu("sp", "sp", 16)]
    c[6] = beq("t6", "zero", CAVE_C + 4 * 6, CAVE_C + 4 * skip_index)
    code = {}
    for base, block in ((CAVE_A, a), (CAVE_B, b), (CAVE_C, c)):
        for i, w in enumerate(block):
            code[base + 4 * i] = w
    patches = {
        0x0017A000: jal(CAVE_A),           # was: jal 0x00167F18
        0x0017A054: jal(CAVE_C),           # was: jal 0x001D0980
        0x00178898: NOP,                   # was: a0 = S
        0x001788A0: j(CAVE_B),             # was: j 0x001D6BA0
    }
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        f"comment=Two-player project, lane A v4 ({variant}, {keep}): every player object uses its own controller;",
        "comment=the first player object stays the game's main player. Every PC online must have this same file.",
    ]
    for addr in sorted(code):
        lines.append(f"patch=1,EE,{addr:08X},word,{code[addr]:08X}")
    for addr in sorted(patches):
        lines.append(f"patch=1,EE,{addr:08X},word,{patches[addr]:08X}")
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    print(len(code), "code words;", len(patches), "hooks ->", out)


if __name__ == "__main__":
    main()
