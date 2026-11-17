import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
NL = chr(10)

# 1. symbols
old = '    "HEAL_BODY": 0x001A2B90,      # inside the per-target routine 0x001A2B50, just behind its unit slot lookup' + NL
new = old + ('    "DIRECT_HIT": 0x0018FAB0,     # script command: deliver this attack to this object (arguments: attack, object ref, 2 values)' + NL +
             '    "HIT_RECORD": 0x0018DB38,     # (attack, target, value, value) -> hit record, 0 if the target may not be hit' + NL +
             '    "HIT_FREE": 0x0018CA10,       # give a hit record back' + NL)
assert old in s
s = s.replace(old, new)

# 2. hook list
old = '    (0x001BA624, 0x0C068A94, "n_heal", "call of the recovery routine 0x001A2A50 when a queued item / Cure takes effect", "jal"),' + NL
new = ('    (0x001BA624, 0x0C068A94, "n_heal", "call of the recovery routine 0x001A2A50 when a queued item takes effect", "jal"),' + NL +
       '    (0x0034EFB8, 0x0018FAB0, "n_cure", "script command table: deliver this attack to this object (how Cure heals)", "table"),' + NL)
assert old in s
s = s.replace(old, new)

# 3. routine
old = '    j HEAL_BODY' + NL + '    move s2,t0' + NL + '"""' + NL
new = ('    j HEAL_BODY' + NL + '    move s2,t0' + NL + NL + '''n_cure:                           # a0 = the script command's arguments: [0] attack, [1] -> +4 = target object, [2], [3]
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    jal DIRECT_HIT                # the game's own routine first
    move s0,a0
    lw t0,0(s0)                   # the attack
    lw t1,0x28(t0)                # its data
    lbu t1,4(t1)
    addiu t1,t1,-5
    sltiu t1,t1,2
    beq t1,zero,n_cu_end          # not a heal (types 5 and 6)
    nop
    lw t2,4(s0)
    lw t2,4(t2)                   # the object the script chose
@DEBUG2@
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)       # player 1's hero
    lui t5,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t5)         # the twin
    beq t5,zero,n_cu_end          # one hero only: nothing to add
    nop
    beq t6,zero,n_cu_end
    nop
    lw t3,0xC(t0)                 # who cast it
    beq t3,t6,n_cu_cast
    nop
    bne t3,t5,n_cu_end            # a friend's Cure: unchanged
    nop
n_cu_cast:
    beq t2,t6,n_cu_do             # a hero's Cure went to the hero: the twin gets it too
    move s1,t5
    bne t2,t5,n_cu_end            # it went to a friend: nothing to add
    nop
    move s1,t6                    # it went to the twin: the hero gets it too
n_cu_do:
    move a0,t0
    move a1,s1
    lw a2,8(s0)
    jal HIT_RECORD                # the game's own hit record (marked "nothing to do" if this attack already reached it)
    lw a3,12(s0)
    beq v0,zero,n_cu_end
    sd v0,24(sp)
    lw t7,0(s1)
    lw t7,0x64(t7)
    move a0,s1
    jalr t7                       # the object's own take-a-hit method, as the game's routine calls it
    move a1,v0
    jal HIT_FREE
    ld a0,24(sp)
n_cu_end:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
"""''' + NL)
assert old in s
s = s.replace(old, new)

# 4. debug text for the new routine and the flag to leave it out
old = '    for flag, label in (("--no-tick", "n_tick"), ("--no-hp", "n_hp"), ("--no-heal", "n_heal")):'
new = '    for flag, label in (("--no-tick", "n_tick"), ("--no-hp", "n_hp"), ("--no-heal", "n_heal"), ("--no-cure", "n_cure")):'
assert old in s
s = s.replace(old, new)

old = '        SYM.update(N_DBG=0x000F2FE0, N_DBG4=0x000F2FE4, N_DBG8=0x000F2FE8, N_DBGC=0x000F2FEC)' + NL
new = (old +
       '        # every heal the script command delivers: a counter and the last three (target, caster) pairs' + NL +
       '        dbg2 = chr(10).join(["    lui t7,%hi(N_RING)", "    addiu t7,t7,%lo(N_RING)", "    lw t3,0(t7)", "    addiu t3,t3,1",' + NL +
       '                             "    sw t3,0(t7)", "    lw t3,12(t7)", "    sw t3,20(t7)", "    lw t3,16(t7)", "    sw t3,24(t7)",' + NL +
       '                             "    lw t3,4(t7)", "    sw t3,12(t7)", "    lw t3,8(t7)", "    sw t3,16(t7)",' + NL +
       '                             "    sw t2,4(t7)", "    lw t3,0xC(t0)", "    sw t3,8(t7)", ""])' + NL +
       '        SYM.update(N_RING=0x000F2F80)' + NL)
assert old in s
s = s.replace(old, new)

old = '    dbg = ""' + NL
new = '    dbg = ""' + NL + '    dbg2 = ""' + NL
assert old in s
s = s.replace(old, new)

old = 'words, syms = assemble(CAVE, SRC.replace("@DEBUG@" + chr(10), dbg), SYM)'
new = 'words, syms = assemble(CAVE, SRC.replace("@DEBUG@" + chr(10), dbg).replace("@DEBUG2@" + chr(10), dbg2), SYM)'
assert old in s
s = s.replace(old, new)

old = 'CAVE_END = 0x000F2FC0'
new = 'CAVE_END = 0x000F2F80     # 0x000F2F80-0x000F2FBF: test-only trace (only written by --debug variants)'
assert old in s
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("ok")
