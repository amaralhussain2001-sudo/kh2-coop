"""One-off: the SIXTY-SECOND GLUE of tools/merge/merge_v7.py (--ownitems), second form (ninth round, part 90).
Seen in run oiE (candidate v95): the game's first refill of a session comes when the room is built, BEFORE the
twin's unit slot has loaded its stats; glue 48's note "the hero's record" (0x000E7E28) is still 0 then, so
oi_refill left player 2's places empty until the next pause menu. The hero's record is always Sora's
(0x0032E020; Roxas has the same one), so oi_init, oi_refill and oi_p2get take that address itself.
(oi_swap keeps the note: it must work on the same record as glue 49's swap of the armour places.)
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownitems2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "(Sora's; Roxas has the same one)" in s:
    raise SystemExit("already there")

a = '''    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record (noted by glue 48)
    beq t9,zero,oi_no
    addiu t2,zero,8
'''
b = '''    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record (Sora's; Roxas has the same one)
    addiu t2,zero,8
'''
assert s.count(a) == 1
s = s.replace(a, b)

a = '''    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record: the count of places
    beq t9,zero,or_out
    nop
    lbu t2,0x12(t9)
'''
b = '''    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record: the count of places
    lbu t2,0x12(t9)
'''
assert s.count(a) == 1
s = s.replace(a, b)

a = '''    bne t7,zero,pg_stock          # (player 2's menu is open: the store holds player 1's things; his stock gets it)
    lw t9,0x7E28(t9)              # the hero's record: the count of places
    beq t9,zero,pg_stock
    nop
    lbu t2,0x12(t9)
'''
b = '''    bne t7,zero,pg_stock          # (player 2's menu is open: the store holds player 1's things; his stock gets it)
    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record: the count of places
    lbu t2,0x12(t9)
'''
assert s.count(a) == 1
s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
