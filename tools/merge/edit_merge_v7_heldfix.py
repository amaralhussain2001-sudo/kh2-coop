"""One-off: tools/merge/merge_v7.py, glues 36 / 38 / 39: THE "HELD BY THIS OBJECT" TEST WAS WRONG.
The paired-move routine 0x00180378 writes victim + 0x240 = the FIRST WORD OF THE CAPTOR'S MOTION PART (captor +
0x140), not the captor object (seen in the post-mortem of run tfpm: an object's + 0x140 word is a pointer into the
file pool). So "hero + 0x240 = the object" was never true, and only the "nearer hero" half of the thirty-sixth
glue did anything (runs gp5 / gp6: player 2's hero in the clash, the command still in player 1's menu).
Now every such test compares hero + 0x240 with the word at object + 0x140 (and wants that word not to be 0).
Run once:  python -I tools/merge/edit_merge_v7_heldfix.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "HELDFIX" in s:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70])
    s = s.replace(old, new)


# thirty-sixth glue (nc_trig): t8 = the object
rep('''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t8,nc_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,nc_twin
    nop
nc_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t8,nc_up
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,nc_body
    nop
nc_up:''', '''    lw t9,0x140(t8)               # HELDFIX: the first word of this object's motion part (what a held hero's + 0x240 holds)
    beq t9,zero,nc_up
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
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
nc_up:''')
# thirty-eighth glue (ro2): s1 = the source object
rep('''    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,s1,r2_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,r2_out
    nop
r2_twin:''', '''    lw t4,0x140(s1)               # the first word of the source's motion part
    beq t4,zero,r2_out
    nop
    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,t4,r2_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,r2_out
    nop
r2_twin:''')
# thirty-ninth glue (nt_held): a0 = the object
rep('''    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,a0,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    nop
    addiu sp,sp,-32''', '''    lw t9,0x140(a0)               # the first word of this object's motion part
    beq t9,zero,nt_old
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    nop
    addiu sp,sp,-32''')
rep('''nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,a0,nt_old''', '''nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nt_old''')
# sizes: three words more in each
rep("NC_AT = 0x000E84C0\nNC_END = 0x000E8600", "NC_AT = 0x000E8A80\nNC_END = 0x000E8BE0")
rep("RH_AT = 0x000E8880\nRH_END = 0x000E88E0", "RH_AT = 0x000E8880\nRH_END = 0x000E88E0")
rep("NT_AT = 0x000E88E0\nNT_END = 0x000E89A0", "NT_AT = 0x000E8BE0\nNT_END = 0x000E8CC0")
# the header's wording
rep("a hero who is held in a paired move by this object (hero + 0x240 = the\nobject, bit 0x4000 of + 0x160) is \"the player\"",
    "a hero who is held in a paired move by this object (hero + 0x240 = the\nword at object + 0x140, bit 0x4000 of + 0x160) is \"the player\"")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
