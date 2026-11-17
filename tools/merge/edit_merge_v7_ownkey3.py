"""One-off: the SIXTY-THIRD GLUE of tools/merge/merge_v7.py (--ownkey), third form (ninth round, part 91).
Seen in run kbG (candidate v99, a room change with two different Keyblades): the files of player 2's Keyblade are
asked for and loaded (number 2303), but the twin holds player 1's. Why: when a room is built, the room data's
second hero can be built FIRST; lane E then takes it for player 1's hero (no player exists yet) and makes it the
twin only when the other hero arrives. So "the twin is being built" (kb_rec) is not known at that moment.
kb_fix (called by kb_tick each step): the twin is a hero, his Keyblade is another one than player 1's, his first
hand holds a weapon that is not bound to his own files (number 2303), and the model file of HIS Keyblade for his
body is loaded with the number 2303: the weapon is ended and built again with his Keyblade (the steps of
kc_menu). One try for each twin object and Keyblade (0x000E7E90 / 94).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "kb_fix" in s:
    raise SystemExit("already there")

a = '''kt_go:
    j TICK_NEXT
    move a0,zero
'''
assert s.count(a) == 1
b = '''kt_go:
    addiu sp,sp,-16
    sd ra,0(sp)
    jal kb_fix
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    j TICK_NEXT
    move a0,zero

kb_fix:                           # each step: the twin holds HIS Keyblade as soon as its files are there
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,kf_out            # (player 2's menu is open)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,kf_out
    lui t8,0x0033
    lhu t5,@KM@(t8)
    addiu t4,zero,0x5034
    bne t5,t4,kf_out
    lhu t5,@KB@(t8)               # his Keyblade
    beq t5,zero,kf_out
    lhu t4,-8160(t8)
    beq t5,t4,kf_out              # the same as player 1's
    lw t3,0xAF8(t6)               # the weapon in his first hand
    beq t3,zero,kf_out
    nop
    lw t2,2560(t3)
    addiu t1,zero,2303
    beq t2,t1,kf_out              # it is bound to his own files already
    lw t2,0x48C(t6)
    beq t2,zero,kf_out
    nop
    lw t2,0x254(t2)               # a hero's body only (1 = Sora, 14 = Roxas)
    addiu t1,zero,1
    beq t2,t1,kf_h
    addiu t1,zero,14
    bne t2,t1,kf_out
    nop
kf_h:
    lw t2,0x7E90(t9)              # tried for this twin object and this Keyblade already
    bne t2,t6,kf_try
    lw t1,0x7E94(t9)
    beq t1,t5,kf_out
    nop
kf_try:
    sw t6,0x7E90(t9)
    sw t5,0x7E94(t9)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s3,16(sp)
    sd s4,24(sp)
    sd s5,32(sp)
    move s0,t6
    jal kc_set                    # his body's weapon set
    move s3,t5
    move a0,v0
    jal 0x00185890                # the weapon object for it and his Keyblade
    move a1,s3
    beq v0,zero,kf_back
    move s5,v0
    jal 0x0016E920                # its entry
    move a0,v0
    beq v0,zero,kf_back
    move a0,v0
    jal 0x0016F470                # the name of its model file
    move a1,zero
    move a0,v0
    jal 0x00170240                # in the pool with the number 2303 ...
    addiu a1,zero,2303
    beq v0,zero,kf_back
    nop
    lbu t7,1(v0)
    addiu t6,zero,3
    bne t7,t6,kf_back             # ... and loaded
    nop
    lw a0,0xAF8(s0)
    sd a0,40(sp)
    jal 0x0019C5D0                # the weapon he holds is ended as the game ends one
    nop
    move s4,v0
    jal 0x00185A28
    ld a0,40(sp)
    sw zero,0xAF8(s0)
    move a0,s0
    move a1,s5
    jal 0x00176168                # and his own is built in his hand
    move a2,zero
    bne s4,zero,kf_back
    nop
    lw a0,0xAF8(s0)
    beq a0,zero,kf_back
    nop
    lw t6,0(a0)
    lw t7,72(t6)
    jalr t7                       # (the game's last step for a new weapon)
    nop
kf_back:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s3,16(sp)
    ld s4,24(sp)
    ld s5,32(sp)
    addiu sp,sp,64
kf_out:
    jr ra
    nop
'''
s = s.replace(a, b)
a = "weapon and files only; kb_ctor (0x00176204)"
assert s.count(a) == 1
s = s.replace(a, "weapon and files only; kb_fix (each step): the twin's first hand gets HIS Keyblade as soon as its files are loaded" + NL + "(a room's second hero can be built before lane E knows that he is the twin); kb_ctor (0x00176204)")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
