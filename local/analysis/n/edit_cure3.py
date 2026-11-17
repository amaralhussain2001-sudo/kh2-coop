"""One-off edit of tools/lane-n/make_down.py: N_CUR (whose update is running), n_party, uniform n_cure."""
import pathlib

p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
NL = chr(10)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)


# ---- 1. n_tick: call the game's update instead of jumping to it, and remember whose update is running ----------
rep("""n_tk_orig:
    j PLAYER_UPDATE
    nop
""", """n_tk_orig:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,%hi(N_CUR)
    jal PLAYER_UPDATE             # the game's own update; while it runs N_CUR = this player object
    sw a0,%lo(N_CUR)(t7)
    lui t7,%hi(N_CUR)
    sw zero,%lo(N_CUR)(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
""")

# ---- 2. n_cure rewritten, n_party added ----------------------------------------------------------------------
i = s.index("n_cure:                           # a0 = the script command's arguments")
j = s.index('"""', i)
new = """n_party:                          # script command "party member number N" (0 = the player, 1 and 2 = the friends)
    lw t0,0(a0)
    bne t0,zero,n_pa_orig
    lui t7,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t7)
    beq t5,zero,n_pa_orig         # one hero only: unchanged
    lui t7,%hi(N_CUR)
    lw t6,%lo(N_CUR)(t7)
    bne t6,t5,n_pa_orig           # asked outside the twin's own update: the engine's player as before
    nop
    jr ra                         # asked by the twin's own scripts (its Cure): "the player" is the twin
    sw t5,0(a0)
n_pa_orig:
    j PARTY_CMD
    nop

n_cure:                           # a0 = the script command's arguments: [0] attack, [1] -> +4 = target object, [2], [3]
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
    lw t3,0xC(t0)                 # who cast it
    beq t3,t6,n_cu_c1
    move t4,t5                    # caster = hero: the other hero is the twin
    bne t3,t5,n_cu_orig           # a friend's Cure: unchanged
    move t4,t6                    # caster = twin: the other hero is player 1's hero
n_cu_c1:
    beq t2,t6,n_cu_go
    nop
    bne t2,t5,n_cu_orig           # a hero's Cure reaching a friend: unchanged
    nop
n_cu_go:                          # a hero's Cure reaching a hero: the caster always, the other hero only when close
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s0,a0
    move s1,t3                    # the caster
    move s2,t4                    # the other hero
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
    c.le.s f0,f1
    bc1t n_cu_r
    nop
    move s2,zero                  # too far away for the other hero
n_cu_r:
    jal n_cu_obj                  # the caster
    move a1,s1
    beq s2,zero,n_cu_end
    nop
    jal n_cu_obj                  # the other hero
    move a1,s2
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

n_cu_obj:                         # deliver the attack of the arguments s0 to the hero object a1, as 0x0018FAB0 does it
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a1,16(sp)
    lw a0,0(s0)
    lw a2,8(s0)
    jal HIT_RECORD                # the game's own hit record (0 if this attack already reached the object)
    lw a3,12(s0)
    beq v0,zero,n_co_out
    sd v0,8(sp)
    ld a0,16(sp)
    lw t7,0(a0)
    lw t7,0x64(t7)
    jalr t7                       # the object's own take-a-hit method
    move a1,v0
    jal HIT_FREE
    ld a0,8(sp)
n_co_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""
s = s[:i] + new + s[j:]

# ---- 3. symbols, hooks, flags ----------------------------------------------------------------------------------
rep('    "HIT_FREE": 0x0018CA10,       # give a hit record back' + NL,
    '    "HIT_FREE": 0x0018CA10,       # give a hit record back' + NL +
    '    "PARTY_CMD": 0x00173E88,      # script command: party member number N (0 = the engine\'s player)' + NL +
    '    "N_CUR": 0x000F2FF0,          # the player object whose update is running (0 outside)' + NL)
rep('    (0x0034EFB8, 0x0018FAB0, "n_cure", "script command table: deliver this attack to this object (how Cure heals)", "table"),' + NL,
    '    (0x0034EFB8, 0x0018FAB0, "n_cure", "script command table: deliver this attack to this object (how Cure heals)", "table"),' + NL +
    '    (0x0034DFE8, 0x00173E88, "n_party", "script command table: party member number N (who a Cure looks at)", "table"),' + NL)
rep('''                        ("--no-cure", "n_cure")):''', '''                        ("--no-cure", "n_cure"), ("--no-party", "n_party")):''')
rep('''         [--no-die] [--no-tick] [--no-hp] [--no-heal] [--no-cure] [--debug] [--kill WHO@FRAME,...]''',
    '''         [--no-die] [--no-tick] [--no-hp] [--no-heal] [--no-cure] [--no-party] [--debug] [--kill WHO@FRAME,...]''')
# debug ring: also remember whose update was running at the newest heal
rep('''"    sw t2,4(t7)", "    lw t3,0xC(t0)", "    sw t3,8(t7)", ""])''',
    '''"    sw t2,4(t7)", "    lw t3,0xC(t0)", "    sw t3,8(t7)",
                             "    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,28(t7)", ""])''')
p.write_text(s, encoding="utf-8")
print("ok")
