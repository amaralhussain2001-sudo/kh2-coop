"""Lane H, part "player trap": what an enemy's AI SCRIPT gets when it asks for "the player".

Almost every AI script holds one call of the engine function "get the player" (script call table 1, number 3),
used for distance and facing checks, and 51 scripts ask for "my last attacker" (table 2, number 88), which falls
back to the player. Both now answer with the hero THIS enemy is dealing with:
  - the hero its target record points to, if that is one of the two heroes;
  - otherwise the same rule as the target search (h_choose).
Only for objects of type BOSS, ZAKO, L_BOSS, L_ZAKO whose own script is running, and only while a twin exists.
Everything else (friends, chests, save points, scenery, the game's native code) still gets player 1's hero.
"""

SYM = {
    "VM_RUN": 0x0016CD48,       # game: run a script context (sets the "running now" globals around it)
    "H_CUR": 0x000F27C0,        # this lane: the object whose AI script is running now (0 outside)
    "TYPE_BOSS": 3, "TYPE_ZAKO": 4, "TYPE_LBOSS": 12, "TYPE_LZAKO": 21,
}

SOURCE = """
h_airun:                            # instead of the call 'run this object's AI script' (the object is in s0)
    lui   t7,%hi(H_CUR)
    sw    s0,%lo(H_CUR)(t7)         # remember whose script runs
    addiu sp,sp,-16
    sd    ra,0(sp)
    jal   VM_RUN
    nop
    lui   t7,%hi(H_CUR)
    sw    zero,%lo(H_CUR)(t7)
    ld    ra,0(sp)
    jr    ra
    addiu sp,sp,16

h_player:                           # instead of 'the engine's player' inside the script call "get the player"
    lui   t7,%hi(G_PLAYER)
    lw    v0,%lo(G_PLAYER)(t7)      # player 1's hero
    lui   t6,%hi(H_CUR)
    lw    t6,%lo(H_CUR)(t6)         # the object whose script is running
    beq   t6,zero,hp_ret
    lui   t5,%hi(V_TWIN)
    lw    t5,%lo(V_TWIN)(t5)
    beq   t5,zero,hp_ret            # no twin: the game's own answer
    nop
    beq   v0,zero,hp_ret
    nop
    lw    t4,8(t6)                  # the object's entry in the object table
    beq   t4,zero,hp_ret
    nop
    lbu   t4,4(t4)                  # its type
    li    t3,TYPE_ZAKO
    beq   t4,t3,hp_enemy
    li    t3,TYPE_BOSS
    beq   t4,t3,hp_enemy
    li    t3,TYPE_LBOSS
    beq   t4,t3,hp_enemy
    li    t3,TYPE_LZAKO
    bne   t4,t3,hp_ret              # not an enemy or boss: player 1's hero
    nop
hp_enemy:
    lw    t4,0x9F4(t6)              # the object this enemy targets now
    beq   t4,t5,hp_twin             # the twin: answer with the twin
    nop
@dbg lui   t3,%hi(H_CNT)
@dbg lw    t2,12(t3)
@dbg addiu t2,t2,1
@dbg sw    t2,12(t3)                # test builds only: count answers "player 1's hero or the rule"
    beq   t4,v0,hp_ret              # player 1's hero
    nop
@dbg lw    t2,8(t3)
@dbg addiu t2,t2,1
@dbg sw    t2,8(t3)                 # test builds only: count answers decided by the rule
    addiu sp,sp,-48                 # no hero targeted yet: the rule
    sd    ra,0(sp)
    sd    s0,8(sp)
    sd    s1,16(sp)
    sd    s2,24(sp)
    move  s0,t6
    move  t7,v0
    move  t6,t5
    jal   h_choose
    move  t5,zero
    ld    ra,0(sp)
    ld    s0,8(sp)
    ld    s1,16(sp)
    ld    s2,24(sp)
    jr    ra
    addiu sp,sp,48
hp_twin:
@dbg lui   t3,%hi(H_CNT)
@dbg lw    t2,4(t3)
@dbg addiu t2,t2,1
@dbg sw    t2,4(t3)                 # test builds only: count answers "the twin"
    move  v0,t5
hp_ret:
    jr    ra
    nop

h_attdef:                           # "my last attacker" when there is none: a0 = the script's first argument
    lw    t6,4(a0)                  # the enemy object
    lui   t7,%hi(G_PLAYER)
    lw    s0,%lo(G_PLAYER)(t7)      # the game's answer: the player (the caller expects it in s0)
    lui   t5,%hi(V_TWIN)
    lw    t5,%lo(V_TWIN)(t5)
    beq   t5,zero,ha_ret
    nop
    lw    t4,0x9F4(t6)
    bne   t4,t5,ha_ret              # this enemy targets the twin: the twin
    nop
    move  s0,t5
ha_ret:
    jr    ra
    nop
"""

HOOKS = [
    (0x0016A96C, "jal", "h_airun", 0x0C05B352, "run an object's AI script: remember the object while its script runs"),
    (0x00171074, "jal", "h_player", 0x0C05AC34, "script call 'get the player' (table 1, number 3): the calling enemy's own hero"),
    (0x0018F458, "jal", "h_attdef", 0x3C0F0035, "script call 'my last attacker' (table 2, number 88), no attacker: the calling enemy's own hero"),
    (0x0018F45C, "word", 0x8E240000, 0x8DF0E948, "delay slot of the line above: a0 = the script's first argument (was: load the engine's player)"),
]
