"""One-off: tools/merge/merge_v7.py, glues 36 and 39: A SHORT MEMORY OF "WHO WAS HELD BY THIS OBJECT".
Run cap6 of the eighth round (candidate v50, both players pressing at Shan-Yu): five of six clashes kept one hero,
one clash had four stray calls for the other hero in its middle. Between two pushes the held hero's "in a paired
move" bit is off for a moment, and the boss's script took the nearer hero in that moment.
Now both routines note the last hold (the object's motion word, which hero, the game's counter) in 0x000E7C0C /
0x000E7C10 / 0x000E7C14, and when nobody is held at the moment but THIS object held a hero less than 90 steps
ago, that hero is still its player.
Run once:  python -I tools/merge/edit_merge_v7_heldmem.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "nc_mtwin" in s:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70])
    s = s.replace(old, new)


# ---- thirty-sixth glue (nc_trig)
rep('''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nc_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,nc_twin
    nop
nc_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nc_up
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,nc_body
    nop
nc_up:
''', '''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nc_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,nc_mtwin
    nop
nc_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nc_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,nc_mp1
    nop
nc_mem:                           # nobody is held at this moment: did THIS object hold a hero a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,nc_up
    lw t2,-11076(t5)              # the game's counter 0x0034D4BC
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,nc_up
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    beq t3,zero,nc_twin           # the twin, less than 90 steps ago
    nop
    b nc_body                     # player 1's hero
    nop
nc_mtwin:                         # the twin is held now: note it
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nc_twin
    sw t3,0x7C14(t7)
nc_mp1:                           # player 1's hero is held now: note it
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nc_body
    sw t3,0x7C14(t7)
nc_up:
''')
# ---- thirty-ninth glue (nt_held)
rep('''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    nop
    addiu sp,sp,-32
''', '''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    lui t7,0x000E
    sw t9,0x7C0C(t7)              # note the hold
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    sw t3,0x7C14(t7)
nt_tw:
    addiu sp,sp,-32
''')
rep('''nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nt_old
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    beq t3,zero,nt_old
    nop
nt_body:
''', '''nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nt_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    beq t3,zero,nt_mem
    lui t7,0x000E
    sw t9,0x7C0C(t7)              # note the hold
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nt_body
    sw t3,0x7C14(t7)
nt_mem:                           # nobody is held at this moment: did THIS object hold a hero a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,nt_old
    lw t2,-11076(t5)
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,nt_old
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    beq t3,zero,nt_tw
    nop
nt_body:
''')
rep("NC_AT = 0x000E8A80\nNC_END = 0x000E8BE0", "NC_AT = 0x000E8E60\nNC_END = 0x000E9040")
rep("NT_AT = 0x000E8BE0\nNT_END = 0x000E8CC0", "NT_AT = 0x000E9040\nNT_END = 0x000E9180")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
