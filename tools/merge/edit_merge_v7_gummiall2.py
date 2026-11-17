"""One-off: the seventy-seventh glue (--gummiall), second form: gx_own reads through weapon + 0x40 only when it is a pointer.
SEEN (run gw1 on v135, route 0 with the kit make_gumweapon.py 499, only player 1 fires): "TLB Miss, pc=0xef17c addr=0x1fcb7 [load]"
= gx_own's lw t3,0x4A4(t3) with t3 = 0x0001F813: for that call, weapon + 0x40 was NOT the weapon's block (the research's chain
holds for some weapons only); then the game jumped to 0x3884 (50 fault lines; run gw3 with both firing: 33 and no end).
NOW: weapon + 0x40 is used only when it is a 4-aligned address in 0x00100000 .. 0x01FFFFFF; else "no player's ship" (0 = player 1).
Run once:  python -I tools/merge/edit_merge_v7_gummiall2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
old = """gx_own:                           # a0 = a weapon -> t2 = 1 / 2 (the ship whose block carries it), 0 = none. t2 .. t5 only
    lw t3,0x40(a0)                # its block
    beq t3,zero,gxo_out
    move t2,zero
    lw t3,0x4A4(t3)               # the block's parent (ship + 0x3E0 for a player's ship)
"""
new = """gx_own:                           # a0 = a weapon -> t2 = 1 / 2 (the ship whose block carries it), 0 = none. t2 .. t5 only
    lw t3,0x40(a0)                # its block (for some weapons this word is no pointer: run gw1)
    move t2,zero
    andi t4,t3,3
    bne t4,zero,gxo_out
    lui t4,0x0010
    sltu t4,t3,t4
    bne t4,zero,gxo_out
    lui t4,0x0200
    sltu t4,t3,t4
    beq t4,zero,gxo_out
    nop
    lw t3,0x4A4(t3)               # the block's parent (ship + 0x3E0 for a player's ship)
"""
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
