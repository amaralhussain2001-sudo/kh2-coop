"""Lane A: 'each player object uses its own controller' patch, version 3.

  python -I tools/lane-a/make_p2pad3.py <outDir> [pad|padplayer]

Background (VERIFIED, see docs/lanes/A-pad-path.md): player objects do not read the controller directly for
normal movement. Each player object's update calls the update of ONE shared control object S (0x01C5F530,
the command-menu controller). S copies the stick and button flags from S->pad (S+0x9E4) and the player object
then reads that copy. S->pad is set once, from the first player object built.

Patch (CRC F266B00B, Kingdom Hearts II Final Mix, SLPM-66675):
 A. Player factory (0x0017A000): the first player object gets logical controller 0, any further one gets 1.
 B. Player method 0x00178888 (calls S's update): just before the call, S->pad = this object's own controller
    pointer (object+0xB38). Variant 'padplayer' also sets S->player (S+0x9E0) = this object.
Code lives in unused memory at 0x000F0000 (zero in every memory dump checked).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mips import RN, jal, j, lui, lw, sw, daddu, NOP  # noqa: E402

GETTER = 0x00167F18
S_UPDATE_WRAPPER = 0x001D6BA0
CAVE_A = 0x000F0000
CAVE_B = 0x000F0020


def sltu(rd, rs, rt):
    return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x2B


def main():
    out = pathlib.Path(sys.argv[1])
    variant = sys.argv[2] if len(sys.argv) > 2 else "pad"
    code = {}
    a = [
        lui("t7", 0x0035),
        lw("t6", 0x2400, "t7"),            # pointer to the last built player object (0 if none)
        j(GETTER),
        sltu("a0", "zero", "t6"),          # controller index = 1 if a player object already exists
    ]
    b = [lw("t6", 0xB38, "a0")]            # this object's own controller pointer   (a0 = object, t7 = S)
    if variant == "padplayer":
        b.append(sw("a0", 0x9E0, "t7"))    # S->player = this object
    b += [
        sw("t6", 0x9E4, "t7"),             # S->pad = this object's controller
        j(S_UPDATE_WRAPPER),
        daddu("a0", "t7", "zero"),         # a0 = S (what the original code passed)
    ]
    for i, w in enumerate(a):
        code[CAVE_A + 4 * i] = w
    for i, w in enumerate(b):
        code[CAVE_B + 4 * i] = w
    patches = {
        0x0017A000: jal(CAVE_A),           # was: jal 0x00167F18 (get logical controller, index in a0)
        0x00178898: NOP,                   # was: a0 = S (moved into the new routine)
        0x001788A0: j(CAVE_B),             # was: j 0x001D6BA0
    }
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        f"comment=Two-player project, lane A v3 ({variant}): every player object uses its own controller.",
        "comment=Every PC in an online game must have this same file (it changes game code).",
    ]
    for addr in sorted(code):
        lines.append(f"patch=1,EE,{addr:08X},word,{code[addr]:08X}")
    for addr in sorted(patches):
        lines.append(f"patch=1,EE,{addr:08X},word,{patches[addr]:08X}")
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
