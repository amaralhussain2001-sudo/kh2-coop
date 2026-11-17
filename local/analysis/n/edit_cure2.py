"""One-off edit of tools/lane-n/make_down.py: n_cure rewritten (the caster always, the other hero only in range)."""
import pathlib

p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
i = s.index("n_cure:                           # a0 = the script command's arguments")
j = s.index('"""', i)
new = """n_cure:                           # a0 = the script command's arguments: [0] attack, [1] -> +4 = target object, [2], [3]
    lw t0,0(a0)                   # the attack
    lw t1,0x28(t0)                # its data
    lbu t1,4(t1)
    addiu t1,t1,-5
    sltiu t1,t1,2
    beq t1,zero,n_cu_orig         # not a heal (types 5 and 6): unchanged
    nop
    lui t7,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t7)         # the twin
    beq t5,zero,n_cu_orig         # one hero only: unchanged
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)       # player 1's hero
    beq t6,zero,n_cu_orig
    lw t2,4(a0)
    lw t2,4(t2)                   # the object the script chose
@DEBUG2@
    bne t2,t6,n_cu_orig           # the script heals a friend: unchanged
    lw t3,0xC(t0)                 # who cast it
    beq t3,t6,n_cu_go
    nop
    bne t3,t5,n_cu_orig           # a friend's Cure on the hero: unchanged
    nop
n_cu_go:                          # a hero's Cure. The script always heals the engine's player (player 1's hero),
    addiu sp,sp,-48               # whoever cast it. Here: the caster always, the other hero only when close.
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s0,a0
    move s1,t5
    lwc1 f0,0x70(t6)              # the game's script only heals friends close to the caster (measured: Goofy is
    lwc1 f1,0x70(t5)              # healed at 280 units and not at 289): the same limit between the two heroes
    sub.s f0,f0,f1
    mul.s f0,f0,f0
    lwc1 f1,0x74(t6)
    lwc1 f2,0x74(t5)
    sub.s f1,f1,f2
    mul.s f1,f1,f1
    add.s f0,f0,f1
    lwc1 f1,0x78(t6)
    lwc1 f2,0x78(t5)
    sub.s f1,f1,f2
    mul.s f1,f1,f1
    add.s f0,f0,f1                # squared distance hero - twin
    lui t7,RANGE2_HI
    ori t7,t7,RANGE2_LO
    mtc1 t7,f1
    li s2,1
    c.le.s f0,f1
    bc1t n_cu_r
    nop
    li s2,0                       # too far away for the other hero
n_cu_r:
    beq t3,s1,n_cu_tw
    nop
    jal DIRECT_HIT                # cast by player 1's hero: the hero as the game does it ...
    move a0,s0
    beq s2,zero,n_cu_end
    nop
    jal n_cu_twin                 # ... and the twin when close
    nop
    b n_cu_end
    nop
n_cu_tw:
    jal n_cu_twin                 # cast by the twin: the twin itself ...
    nop
    beq s2,zero,n_cu_end
    nop
    jal DIRECT_HIT                # ... and the hero (the script's own target) when close
    move a0,s0
n_cu_end:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
n_cu_orig:
    j DIRECT_HIT
    nop

n_cu_twin:                        # deliver the attack of the arguments s0 to the twin s1, as 0x0018FAB0 does it
    addiu sp,sp,-16
    sd ra,0(sp)
    lw a0,0(s0)
    move a1,s1
    lw a2,8(s0)
    jal HIT_RECORD                # the game's own hit record (0 if the twin may not be hit now)
    lw a3,12(s0)
    beq v0,zero,n_ct_out
    sd v0,8(sp)
    lw t7,0(s1)
    lw t7,0x64(t7)
    move a0,s1
    jalr t7                       # the object's own take-a-hit method
    move a1,v0
    jal HIT_FREE
    ld a0,8(sp)
n_ct_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
s = s[:i] + new + s[j:]
p.write_text(s, encoding="utf-8")
print("ok")
