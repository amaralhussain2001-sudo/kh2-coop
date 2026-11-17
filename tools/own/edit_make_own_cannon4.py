"""One-off: tools/own/make_own.py, the option --cannon2view (ninth round, job 5), third form.
Seen in runs cnA / cnB: the game's own cannon view is a STILL view from behind the cannon (player 1's cannon
object stands still, only its barrel turns), but the second cannon, made at run time, turns as a whole with
player 2's stick, so a camera worked out from ITS place and turn swung about and sat inside the cannon.
Now: the game works the view out from player 1's cannon for both cameras, and player 2's camera is then moved by
the way from player 1's cannon to his own (the four places the cannon camera writes: camera + 0, + 16, + 96,
+ 128). So each player has the game's still view, centred behind his own cannon.
cn_cam's block moves to 0x000F7400 .. 0x000F74FF (lane V2's old marker room, free behind the ring glue).
Without the option the builder writes what it wrote before, bit for bit.
The record of the edit; run once:
  python -I tools/own/edit_make_own_cannon4.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "make_own.py"
s = p.read_text(encoding="utf-8")
if "cc_add:" in s:
    raise SystemExit("already there")
a = s.index("CN_AT = 0x000F5E90")
b = s.index('"""' + NL, s.index('CN_SRC = """', a) + 12) + len('"""' + NL)
new = '''CN_AT = 0x000F7400                # (--cannon2view) the toy cannon's camera for each player: 0x000F7400-0x000F74FF
CN_END = 0x000F7500
CN_SRC = """
cn_cam:                           # the call at 0x00140C9C (camera kind 10 = the toy cannon's): a0 = the camera
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    lui t1,0x0035
    lw t9,-5816(t1)               # the engine's player (player 1's cannon: it stands still, only its barrel turns)
    beq t9,zero,cc_run
    lui t1,0x004F
    sw t9,0x35A0(t1)              # 0x004F35A0: the cannon the game works the view out from
cc_run:
    jal 0x001589D0
    nop
    ld a0,8(sp)
    lui t7,0x000F
    lw t0,0x6F0C(t7)              # not 0: player 2's camera is in the game's camera memory
    beq t0,zero,cc_out
    lw t8,0x05CC(t7)              # the twin
    beq t8,zero,cc_out
    lui t1,0x0035
    lw t9,-5816(t1)
    beq t9,zero,cc_out
    nop
    lwc1 f0,0x70(t8)              # player 2's picture: the same view, moved by the way from player 1's cannon to his
    lwc1 f1,0x70(t9)
    lwc1 f2,0x74(t8)
    lwc1 f3,0x74(t9)
    lwc1 f4,0x78(t8)
    lwc1 f5,0x78(t9)
    sub.s f0,f0,f1
    sub.s f2,f2,f3
    sub.s f4,f4,f5
    jal cc_add
    move t3,a0                    # camera + 0: the aim point
    jal cc_add
    addiu t3,a0,16                # camera + 16: the eye
    jal cc_add
    addiu t3,a0,96                # camera + 96, + 128: the same two as the cannon camera wrote them
    jal cc_add
    addiu t3,a0,128
cc_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
cc_add:                           # t3 = a place (x, y, z)
    lwc1 f6,0(t3)
    lwc1 f7,4(t3)
    lwc1 f8,8(t3)
    add.s f6,f6,f0
    add.s f7,f7,f2
    add.s f8,f8,f4
    swc1 f6,0(t3)
    swc1 f7,4(t3)
    jr ra
    swc1 f8,8(t3)
"""
'''
s = s[:a] + new + s[b:]
with open(p, "w", encoding="utf-8", newline=chr(13) + chr(10)) as f:      # the file has CRLF line ends
    f.write(s)
print("ok")
