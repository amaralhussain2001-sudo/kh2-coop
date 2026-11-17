"""Lane A: write the 'second player object listens to controller 2' patch file.

  python -I tools/lane-a/make_p2pad.py <outDir> [v1|v2]

v1: the player factory asks for logical controller 1 (pad 2) when a player object already exists.
v2: v1 + after the second object is built, the game's "current player" pointer is put back to the first object.

What it changes (CRC F266B00B, Kingdom Hearts II Final Mix, SLPM-66675):
  0x0017A000  jal 0x00167F18  ->  jal 0x000F0000      (player factory: choose the controller index)
  0x0017A054  jal 0x001D0980  ->  jal 0x000F0020      (v2 only: wrap the player constructor call)
  0x000F0000..                 small routines in unused memory (zero in every dump checked)
  0x000F0100                   one word of scratch data (v2)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mips import RN, addiu, jal, j, jr, lui, lw, sw, sd, ld, beq, NOP  # noqa: E402

GETTER = 0x00167F18       # returns &logical_controller[a0]
PLAYER_CTOR = 0x001D0980  # standard player object constructor
CUR_PLAYER_HI, CUR_PLAYER_LO = 0x0035, 0x2400   # 0x00352400: pointer to the last constructed player object
CAVE = 0x000F0000
SCRATCH_HI, SCRATCH_LO = 0x000F, 0x0100


def sltu(rd, rs, rt):
    return (RN[rs] << 21) | (RN[rt] << 16) | (RN[rd] << 11) | 0x2B


def build(version):
    code = {}
    pc = CAVE
    # --- cave 1: choose the controller index -------------------------------------------------
    c1 = [
        lui("t7", CUR_PLAYER_HI),
        lw("t6", CUR_PLAYER_LO, "t7"),          # t6 = existing player object (0 if none)
    ]
    if version == "v2":
        c1 += [lui("t5", SCRATCH_HI), sw("t6", SCRATCH_LO, "t5")]   # remember it for cave 2
    c1 += [
        j(GETTER),                               # tail call: returns to the factory
        sltu("a0", "zero", "t6"),               # delay slot: a0 = 1 if a player already exists, else 0
    ]
    for w in c1:
        code[pc] = w
        pc += 4
    patches = {0x0017A000: jal(CAVE)}
    if version == "v2":
        cave2 = CAVE + 0x20
        pc = cave2
        skip = cave2 + 4 * 9
        c2 = [
            addiu("sp", "sp", -16),
            sd("ra", 0, "sp"),
            jal(PLAYER_CTOR),
            NOP,
            lui("t5", SCRATCH_HI),
            lw("t6", SCRATCH_LO, "t5"),          # the player that existed before this construction
            beq("t6", "zero", cave2 + 4 * 6, skip),
            lui("t7", CUR_PLAYER_HI),            # delay slot
            sw("t6", CUR_PLAYER_LO, "t7"),       # current player = the first object again
            ld("ra", 0, "sp"),                   # skip:
            jr("ra"),
            addiu("sp", "sp", 16),
        ]
        for w in c2:
            code[pc] = w
            pc += 4
        patches[0x0017A054] = jal(cave2)
    return code, patches


def main():
    out = pathlib.Path(sys.argv[1])
    version = sys.argv[2] if len(sys.argv) > 2 else "v1"
    code, patches = build(version)
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        f"comment=Two-player project, lane A, {version}: the second player object reads controller 2.",
        "comment=Every PC in an online game must have this same file (it changes game code).",
    ]
    for a in sorted(code):
        lines.append(f"patch=1,EE,{a:08X},word,{code[a]:08X}")
    for a in sorted(patches):
        lines.append(f"patch=1,EE,{a:08X},word,{patches[a]:08X}")
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
