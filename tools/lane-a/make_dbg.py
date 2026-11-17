"""Lane A: debug patch. The player factory logs, for every player object it builds, the 'current player'
pointer seen at that moment and the object id, into unused memory at 0x000F0100.. (count at 0x000F0100,
pointers from 0x000F0110, ids from 0x000F0150). Controller choice is NOT changed (always controller 1).

  python -I tools/lane-a/make_dbg.py <outDir>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mips import RN, addiu, addu, jal, j, lui, lw, sw  # noqa: E402


def sll(rd, rt, sa):
    return (RN[rt] << 16) | (RN[rd] << 11) | (sa << 6)


CAVE = 0x000F0000
code = [
    lui("t7", 0x35),
    lw("t6", 0x2400, "t7"),        # current player pointer
    lui("t5", 0x000F),
    lw("t4", 0x0100, "t5"),        # count
    sll("t3", "t4", 2),
    addu("t3", "t3", "t5"),
    sw("t6", 0x0110, "t3"),
    lw("t2", 0, "s1"),             # object id (s1 = object entry pointer in the factory)
    sw("t2", 0x0150, "t3"),
    addiu("t4", "t4", 1),
    sw("t4", 0x0100, "t5"),
    j(0x00167F18),
    0x0000202D,                    # delay slot: a0 = 0 (unchanged behaviour)
]
out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B) - lane A debug",
         "comment=DEBUG ONLY: logs player object constructions to 0x000F0100.."]
for i, w in enumerate(code):
    lines.append(f"patch=1,EE,{CAVE + 4 * i:08X},word,{w:08X}")
lines.append(f"patch=1,EE,0017A000,word,{jal(CAVE):08X}")
(out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
print(len(code), "words")
