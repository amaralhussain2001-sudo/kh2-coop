"""Lane N patch generator: "down like Goofy" for the two heroes (CRC F266B00B, KH2 Final Mix SLPM-66675).

  python -I tools/lane-n/make_down.py <outDir> [--base DIR] [--time N] [--cure-range N] [--extra FILE]
         [--no-die] [--no-tick] [--no-hp] [--no-heal] [--no-cure] [--no-party] [--debug] [--kill WHO@FRAME,...]

  --cure-range N  how close the other hero must be to the caster to share a hero's Cure (default 285, the
                  distance at which the game's own Cure stops reaching a friend)
  --no-...   leave one of the five hooks out (test variants)
  --debug    TEST ONLY: trace words at 0x000F2F80-0x000F2FBF and 0x000F2FE0-0x000F2FEF
  --kill     TEST ONLY: WHO = hero | twin | f0 | f1 loses all HP at that session frame (the same on both PCs)

  --time N   recovery time in 1/60 s (default 2700 = 45 s, Goofy's own value); shorter values are for tests only
  --extra    append test-only lines (tools/lane-n/make_testlines.py); never for the real game patch

Output: <outDir>/SLPM-66675_F266B00B.pnach = the base patch's lines (default patches/merged-v2, unchanged) + lane N's
lines, and <outDir>/listing.txt (every lane N word with its meaning).

What lane N adds. Three words of the main player class table 0x00352410 and one call site are changed; no other
game code is overwritten.
  n_die   table + 0x5C (was 0x001D0D60, the player's "HP reached 0" routine)
          A hero that falls while the OTHER hero is still up goes DOWN: the game's own base routine (commands off,
          cry, "fallen" flag), the lying pose and dead action state of the normal defeat, and a recovery timer.
          No Game Over is started. With one hero only, or when the other hero is already down, the game's own
          routine runs unchanged (Game Over, mission rule, King Mickey).
  n_tick  table + 0x0C (was 0x00178758, the player's per-frame update)
          While a hero is down its timer runs exactly like a fallen friend's (0x0017DCC0: frame time, 8 times
          faster outside a fight); at 0 the friend's own recovery routine 0x0017DE70 is called (HP change of
          max HP x table factor, which comes back through n_hp).
  n_hp    table + 0x78 (was 0x0017A480, the player's HP-change routine)
          A positive HP change on a down hero (Potion, Cure, the timer) revives it the way the game revives a
          friend (0x0017E138: flag off, amount scaled as for a friend) and the way the game itself puts a player
          back on its feet (0x00179F10: action state 0, control object; 0x001D6AB0: commands on).
  n_heal  call site 0x001BA624 (was jal 0x001A2A50, "a queued item or Cure takes effect")
          The game heals by character id, so the twin (same id as player 1's hero) was never reached.
          Party-wide effects (Cure, Mega-Potion ...): the game's routine as before, then the same effect on the
          twin's own unit slot. One-target effects on the heroes' id: used by the hero (or a friend) they go to
          the hero, unless the twin is down and the hero is not; used by the twin they go to the twin, unless the
          hero is down.

Code cave 0x000F2800-0x000F2FBF, variables 0x000F2FC0-0x000F2FDF (must be zero at boot; not written by the file):
  +0x00 / +0x04  recovery timer in 1/60 s (float): hero / twin
  +0x08 / +0x0C  1 while down by lane N's rule: hero / twin
  +0x10 / +0x14  number of falls handled: hero / twin        (evidence counters)
  +0x18 / +0x1C  number of revives handled: hero / twin
"hero" = the engine's player object (0x0034E948, kept on player 1's hero by lane E); "twin" = lane E's 0x000F05CC.
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402
import mips  # noqa: E402

ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"
CAVE = 0x000F2800
CAVE_END = 0x000F2F80     # 0x000F2F80-0x000F2FBF: test-only trace (only written by --debug variants)

SYM = {
    "G_PLAYER": 0x0034E948,       # engine's player object (player 1's hero)
    "V_TWIN": 0x000F05CC,         # lane E: the twin object, 0 if none
    "N_VARS": 0x000F2FC0,
    "DT": 0x00349E10,             # frame time in 1/60 s (float; 2.0 in play)
    "BTL": 0x01C61958,            # battle state (0 = no fight)
    "BTABLE": 0x00352130,         # pointer to the battle parameter table
    "BLEND": 0x0036C578,          # float the game's friend revive uses as blend time
    "PLAYER_DIE": 0x001D0D60,     # player class: HP reached 0 (decides Game Over)
    "PLAYER_UPDATE": 0x00178758,  # player class: per-frame update
    "PLAYER_HP": 0x0017A480,      # player class: HP change
    "BASE_DIE": 0x00179E18,       # player base: commands off, cry, fallen flag
    "DIE_LOOK": 0x001D0EB8,       # motion 0x36 (lying) and action state 0x29 (dead), as in the game's own defeat
    "FRIEND_RECOVER": 0x0017DE70, # friend: timed recovery = HP change of max HP x table factor
    "FRIEND_REVIVE": 0x0017E138,  # friend: revive on a heal (flag off), returns the amount scaled as for a friend
    "SET_MOTION": 0x0017F488,     # (f12 blend, f13, a0 = object + 0x140, a1 = motion number)
    "QUEUE_MOTION": 0x0017F5E0,   # (f12, f13, a0 = object + 0x140, a1 = next motion, a2)
    "PLAYER_UP": 0x00179F10,      # player: fallen flag off, action state 0, control object's player = this object
    "CMD_ON": 0x001D6AB0,         # control object: commands on (the opposite of 0x001D6A80)
    "RECOVER": 0x001A2A50,        # apply a recovery effect: (effect id, target status id, user status id, boost)
    "IS_PARTY": 0x001A3888,       # is the effect party-wide (ids 5, 6, 7, 0x83)?
    "ITEMDATA": 0x001A80C8,       # effect id -> effect data
    "HEAL_BODY": 0x001A2B90,      # inside the per-target routine 0x001A2B50, just behind its unit slot lookup
    "DIRECT_HIT": 0x0018FAB0,     # script command: deliver this attack to this object (arguments: attack, object ref, 2 values)
    "HIT_RECORD": 0x0018DB38,     # (attack, target, value, value) -> hit record, 0 if the target may not be hit
    "HIT_FREE": 0x0018CA10,       # give a hit record back
    "PARTY_CMD": 0x00173E88,      # script command: party member number N (0 = the engine's player)
    "SCRIPT_THREAD": 0x0034D8A4,  # the script thread being run (set by 0x0016CD48); +0x38 = the object it belongs to
}

HOOKS = [  # address, original word, routine label, meaning, kind ("table" = class table word, "jal" = call site)
    (0x0035246C, 0x001D0D60, "n_die", "player class table +0x5C: HP reached 0", "table"),
    (0x0035241C, 0x00178758, "n_tick", "player class table +0x0C: per-frame update", "table"),
    (0x00352488, 0x0017A480, "n_hp", "player class table +0x78: HP change", "table"),
    (0x001BA624, 0x0C068A94, "n_heal", "call of the recovery routine 0x001A2A50 when a queued item takes effect", "jal"),
    (0x0034EFB8, 0x0018FAB0, "n_cure", "script command table: deliver this attack to this object (how Cure heals)", "table"),
    (0x0034DFE8, 0x00173E88, "n_party", "script command table: party member number N (who a Cure looks at)", "table"),
]

SRC = """
n_die:                            # a0 = player object whose HP reached 0
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)       # player 1's hero
    lui t5,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t5)         # the twin
    beq t5,zero,n_die_orig        # one hero only: the game's own defeat
    nop
    beq t6,zero,n_die_orig
    nop
    beq a0,t6,n_die_h
    nop
    bne a0,t5,n_die_orig          # some other player object: unchanged
    nop
    move t4,t6                    # a0 is the twin: the other one is the hero
    b n_die_chk
    li t3,4
n_die_h:
    move t4,t5                    # a0 is the hero: the other one is the twin
    li t3,0
n_die_chk:
    lw t2,0x7F8(t4)
    andi t2,t2,4
    bne t2,zero,n_die_orig        # the other hero is already down: both down = the game's own defeat
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    move s0,a0
    jal BASE_DIE                  # commands off, cry, fallen flag (as every defeat starts)
    move s1,t3
    jal DIE_LOOK                  # lying pose and the dead action state of the normal defeat
    move a0,s0
    lui t7,TIME_HI                # recovery time: Goofy's own table value (2700 = 45 s); a player's own is 0
    ori t7,t7,TIME_LO
    mtc1 t7,f0
    lw t6,0x48C(s0)
    lwc1 f1,0x228(t6)             # x the unit's factor, as in the friend formula (0x0017E108)
    mul.s f0,f0,f1
    lui t5,%hi(N_VARS)
    addiu t5,t5,%lo(N_VARS)
    addu t5,t5,s1
    swc1 f0,0(t5)                 # timer
    li t4,1
    sw t4,8(t5)                   # down
    lw t4,0x10(t5)
    addiu t4,t4,1
    sw t4,0x10(t5)                # count the fall
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
n_die_orig:
    j PLAYER_DIE
    nop

n_tick:                           # a0 = player object, every frame, before the game's own update
@KILL@
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    lui t5,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t5)
    beq a0,t6,n_tk_role
    li t3,0
    bne a0,t5,n_tk_orig
    nop
    li t3,4
n_tk_role:
    lui t4,%hi(N_VARS)
    addiu t4,t4,%lo(N_VARS)
    addu t4,t4,t3
    lw t2,8(t4)
    beq t2,zero,n_tk_orig         # not down
    nop
    lw t2,0x7F8(a0)
    andi t2,t2,4
    bne t2,zero,n_tk_dead
    nop
    b n_tk_orig                   # a newly built object (room change, Continue): forget the state
    sw zero,8(t4)
n_tk_dead:
    lui t7,%hi(DT)
    lwc1 f1,%lo(DT)(t7)           # frame time
    lui t6,%hi(BTL)
    lw t6,%lo(BTL)(t6)
    bne t6,zero,n_tk_sub
    nop
    lui t6,%hi(BTABLE)            # outside a fight the timer runs faster, as for a friend
    lw t6,%lo(BTABLE)(t6)
    lwc1 f2,0x5C(t6)
    mul.s f1,f1,f2
n_tk_sub:
    lwc1 f0,0(t4)
    sub.s f0,f0,f1
    swc1 f0,0(t4)
    mtc1 zero,f2
    c.le.s f0,f2
    bc1f n_tk_orig
    nop
    addiu sp,sp,-16               # time is up: the friend's own recovery (comes back through n_hp)
    sd ra,0(sp)
    sd a0,8(sp)
    jal FRIEND_RECOVER
    nop
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
n_tk_orig:
    j PLAYER_UPDATE
    nop

n_hp:                             # a0 = player object, a1 = HP change, a2 = gauge (0 = HP), a3 = flag
    blez a1,n_hp_orig             # only a heal can bring a hero back
    nop
@DEBUG@
    bne a2,zero,n_hp_orig
    nop
    lw t7,0x7F8(a0)
    andi t7,t7,4
    beq t7,zero,n_hp_orig         # not fallen
    nop
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    lui t5,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t5)
    beq a0,t6,n_hp_role
    li t3,0
    bne a0,t5,n_hp_orig
    nop
    li t3,4
n_hp_role:
    lui t4,%hi(N_VARS)
    addiu t4,t4,%lo(N_VARS)
    addu t4,t4,t3
    lw t2,8(t4)
    beq t2,zero,n_hp_orig         # fallen by the game's own defeat (Game Over is running): unchanged
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    move s0,a0
    jal FRIEND_REVIVE             # fallen flag off, v0 = amount scaled as for a friend
    move s1,t4
    sd v0,40(sp)
    lui t7,%hi(BLEND)             # a hero's motion set has no friend get-up motion (0x37): play the hero's own
    lwc1 f12,%lo(BLEND)(t7)       # recover motion (6), then idle, with the blend time the game's revive uses
    mtc1 zero,f13
    addiu a0,s0,0x140
    jal SET_MOTION
    li a1,6
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,s0,0x140
    move a1,zero
    jal QUEUE_MOTION
    move a2,zero
    jal PLAYER_UP                 # the game's own "player is up again": action state 0 (the defeat put it in
    move a0,s0                    # state 0x29, which takes no input), control object -> this hero
    jal CMD_ON                    # this hero's control object takes commands again (BASE_DIE switched them off)
    lw a0,0xB3C(s0)
    ld v0,40(sp)
    sw zero,8(s1)                 # no longer down
    lw t2,0x18(s1)
    addiu t2,t2,1
    sw t2,0x18(s1)                # count the revive
    bgtz v0,n_hp_amt
    nop
    li v0,1                       # never come back with 0 HP
n_hp_amt:
    move a1,v0
    move a0,s0
    ld a2,24(sp)
    ld a3,32(sp)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    addiu sp,sp,48
n_hp_orig:
    j PLAYER_HP
    nop

n_heal:                           # a0 = effect id, a1 = target status id, a2 = user status id, a3 = boost;
                                  # s1 (the caller's) = the queued recovery record, +8 = the user's object
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    beq t6,zero,n_he_orig         # one hero only: the game's own routine
    nop
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s2,16(sp)
    sd s3,24(sp)
    sd s4,32(sp)
    sd s5,40(sp)
    move s0,a0
    move s2,a1
    move s3,a2
    move s4,a3
    jal IS_PARTY
    move s5,t6                    # the twin
    bne v0,zero,n_he_party
    nop
    lw t7,8(s5)                   # one target: is it the heroes' status id?
    lhu t7,0x4C(t7)
    bne s2,t7,n_he_game           # a friend is the target: the game's own routine
    nop
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)       # player 1's hero
    lw t5,8(s1)                   # the user's object
    lw t4,0x7F8(s5)
    andi t4,t4,4                  # twin down?
    lw t3,0x7F8(t6)
    andi t3,t3,4                  # hero down?
    beq t5,s5,n_he_utwin
    nop
    beq t4,zero,n_he_game         # used by the hero (or a friend): the twin gets it only if the twin is down
    nop
    bne t3,zero,n_he_game         # ... and the hero is not
    nop
    b n_he_twin
    nop
n_he_utwin:
    bne t3,zero,n_he_game         # used by the twin: on itself, unless the hero is down (then the hero gets it)
    nop
n_he_twin:
    jal n_he_slot
    nop
    b n_he_done
    move v0,zero
n_he_party:
    move a0,s0
    move a1,s2
    move a2,s3
    jal RECOVER                   # every party member, the game's way (the hero's slot for the heroes' id)
    move a3,s4
    sd v0,48(sp)
    lw t7,8(s5)
    jal n_he_slot                 # and the same effect on the twin's own slot
    lhu s2,0x4C(t7)
    b n_he_done
    ld v0,48(sp)
n_he_game:
    move a0,s0
    move a1,s2
    move a2,s3
    jal RECOVER
    move a3,s4
n_he_done:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s2,16(sp)
    ld s3,24(sp)
    ld s4,32(sp)
    ld s5,40(sp)
    jr ra
    addiu sp,sp,64
n_he_orig:
    j RECOVER
    nop

n_he_slot:                        # effect s0 on the twin's (s5) own unit slot; target id s2, user id s3, boost s4
    addiu sp,sp,-16
    sd ra,0(sp)
    jal ITEMDATA
    move a0,s0
    move a0,v0
    move a1,s2
    move a2,s3
    move a3,s4
    lw t0,0x48C(s5)
    beq t0,zero,n_hs_out
    nop
    lw t1,0x258(t0)
    addiu t1,t1,1
    sw t1,0x258(t0)               # one more reference: the game's routine releases one at its end
    jal n_he_enter
    nop
n_hs_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
n_he_enter:                       # the stack frame of 0x001A2B50, with the unit slot already chosen (t0)
    addiu sp,sp,-48
    sd s3,24(sp)
    sd s1,8(sp)
    sd s0,0(sp)
    sd s4,32(sp)
    sd s2,16(sp)
    sd ra,40(sp)
    move s3,a0
    move s1,a1
    move s0,a2
    move s4,a3
    j HEAL_BODY
    move s2,t0

n_party:                          # script command "party member number N" (0 = the player, 1 and 2 = the friends)
@DEBUG3@
    lw t0,0(a0)
    bne t0,zero,n_pa_orig         # the friends: unchanged
    lui t7,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t7)
    beq t5,zero,n_pa_orig         # one hero only: unchanged
    lui t7,%hi(SCRIPT_THREAD)
    lw t6,%lo(SCRIPT_THREAD)(t7)  # the script thread that is running now
    beq t6,zero,n_pa_orig
    nop
    lw t6,0x38(t6)                # the object that script belongs to (a Cure's: its caster)
    bne t6,t5,n_pa_orig           # not the twin's script: the engine's player as before
    nop
    jr ra                         # the twin's own script (its Cure): "the player" is the twin
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


KILL_SRC = """    lui t7,%hi(G_PLAYER)          # TEST ONLY (--kill): once per step, when the game's counter reaches a table
    lw t6,%lo(G_PLAYER)(t7)       # entry, that unit loses all its HP through its own HP-change method
    bne a0,t6,n_k_skip
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd s0,16(sp)
    lui s0,%hi(n_k_table)
    addiu s0,s0,%lo(n_k_table)
n_k_loop:
    lw t0,0(s0)                   # counter value of this entry (0 = end of the table)
    beq t0,zero,n_k_done
    nop
    lui t7,%hi(CNT)
    lw t2,%lo(CNT)(t7)
    subu t2,t2,t0
    sltiu t2,t2,2                 # counter is at the entry's value or one behind it
    beq t2,zero,n_k_next
    nop
    lw t4,4(s0)                   # who: 0 hero, 1 twin, 2 / 3 the friends
    lui t7,%hi(G_PLAYER)
    lw a0,%lo(G_PLAYER)(t7)
    beq t4,zero,n_k_go
    nop
    lui t7,%hi(V_TWIN)
    lw a0,%lo(V_TWIN)(t7)
    addiu t5,t4,-1
    beq t5,zero,n_k_go
    nop
    sll t5,t4,2
    lui t7,%hi(FRIENDS)
    addiu t7,t7,%lo(FRIENDS)
    addu t7,t7,t5
    lw a0,-8(t7)
n_k_go:
    beq a0,zero,n_k_next
    nop
    lw t7,0x7F8(a0)
    andi t7,t7,4
    bne t7,zero,n_k_next          # already fallen
    nop
    lw t7,0(a0)
    lw t7,0x78(t7)
    addiu a1,zero,-9999
    move a2,zero
    jalr t7
    move a3,zero
n_k_next:
    b n_k_loop
    addiu s0,s0,8
n_k_done:
    ld ra,0(sp)
    ld a0,8(sp)
    ld s0,16(sp)
    addiu sp,sp,32
n_k_skip:
"""


def main():
    args = sys.argv[1:]
    out = pathlib.Path(args[0])
    base = ROOT / "patches" / "merged-v2"
    if "--base" in args:
        base = pathlib.Path(args[args.index("--base") + 1])
    skip = set()
    for flag, label in (("--no-die", "n_die"), ("--no-tick", "n_tick"), ("--no-hp", "n_hp"), ("--no-heal", "n_heal"),
                        ("--no-cure", "n_cure"), ("--no-party", "n_party")):
        if flag in args:
            skip.add(label)
    extra = []
    while "--extra" in args:
        i = args.index("--extra")
        extra += [x for x in pathlib.Path(args[i + 1]).read_text().splitlines() if x.strip()]
        del args[i:i + 2]
    secs60 = 2700.0
    if "--time" in args:
        secs60 = float(args[args.index("--time") + 1])
    bits = struct.unpack("<I", struct.pack("<f", secs60))[0]
    SYM["TIME_HI"], SYM["TIME_LO"] = bits >> 16, bits & 0xFFFF

    kill_src, kill_tab = "", ""
    if "--kill" in args:       # TEST ONLY: WHO@FRAME,... makes hero | twin | f0 | f1 (friends) lose all HP at that frame
        i = args.index("--kill")
        ents = []
        for item in args[i + 1].split(","):
            who, _, fr = item.partition("@")
            ents.append((int(fr) - 152, {"hero": 0, "twin": 1, "f0": 2, "f1": 3}[who]))
        del args[i:i + 2]
        kill_src = KILL_SRC
        NL = chr(10)
        kill_tab = NL + "n_k_table:" + NL + "".join("    .word %d" % c + NL + "    .word %d" % w + NL for c, w in ents) + "    .word 0" + NL
        SYM.update(CNT=0x0034D4BC, FRIENDS=0x01C60528)
    rng = 285.0
    if "--cure-range" in args:
        rng = float(args[args.index("--cure-range") + 1])
    bits = struct.unpack("<I", struct.pack("<f", rng * rng))[0]
    SYM["RANGE2_HI"], SYM["RANGE2_LO"] = bits >> 16, bits & 0xFFFF
    dbg = ""
    dbg2 = ""
    dbg3 = ""
    if "--debug" in args:      # TEST ONLY: remember who healed a player object last (return addresses, amount, object)
        # only for a hit delivered by 0x00186D48 (ra = 0x00186DD8): the return address of whoever called the
        # object's take-a-hit method (three frames up: 48 + 32 + 8), the attacker object, the amount, the target
        dbg = chr(10).join(["    lui t7,%hi(N_DBG)", "    lui t6,0x0018", "    ori t6,t6,0x6DD8",
                            "    bne ra,t6,n_dbg_end", "    nop", "    lw t6,88(sp)", "    sw t6,%lo(N_DBG)(t7)",
                            "    lw t6,0x1C(s0)", "    lw t6,0xC(t6)", "    sw t6,%lo(N_DBG4)(t7)",
                            "    sw a1,%lo(N_DBG8)(t7)", "    sw a0,%lo(N_DBGC)(t7)", "n_dbg_end:", ""])
        SYM.update(N_DBG=0x000F2FE0, N_DBG4=0x000F2FE4, N_DBG8=0x000F2FE8, N_DBGC=0x000F2FEC)
        # every heal the script command delivers: a counter and the last three (target, caster) pairs
        dbg2 = chr(10).join(["    lui t7,%hi(N_RING)", "    addiu t7,t7,%lo(N_RING)", "    lw t3,0(t7)", "    addiu t3,t3,1",
                             "    sw t3,0(t7)", "    lw t3,12(t7)", "    sw t3,20(t7)", "    lw t3,16(t7)", "    sw t3,24(t7)",
                             "    lw t3,4(t7)", "    sw t3,12(t7)", "    lw t3,8(t7)", "    sw t3,16(t7)",
                             "    sw t2,4(t7)", "    lw t3,0xC(t0)", "    sw t3,8(t7)",
                             "    sw ra,32(t7)", "    lw t3,4(a0)", "    sw t3,36(t7)", "    lw t3,0(t3)", "    sw t3,40(t7)", ""])
        # every call of the party-member script command: counter, index asked, caller, whose update was running
        dbg3 = chr(10).join(["    lui t7,%hi(N_RING)", "    addiu t7,t7,%lo(N_RING)", "    lw t3,44(t7)", "    addiu t3,t3,1",
                             "    sw t3,44(t7)", "    lw t3,0(a0)", "    sw t3,48(t7)",
                             "    lui t3,0x0035", "    lw t4,-0x2760(t3)", "    sw t4,52(t7)",      # 0x0034D8A0 root thread
                             "    lw t4,-0x275C(t3)", "    sw t4,56(t7)",                            # 0x0034D8A4 this thread
                             "    lui t3,%hi(G_PLAYER)", "    lw t3,%lo(G_PLAYER)(t3)", "    lw t3,0x484(t3)", "    sw t3,60(t7)",
                             "    lui t3,%hi(V_TWIN)", "    lw t3,%lo(V_TWIN)(t3)", "    lw t3,0x484(t3)", "    sw t3,28(t7)", ""])
        SYM.update(N_RING=0x000F2F80)
    elf = mips.Elf(str(ELF))
    words, syms = assemble(CAVE, (SRC + kill_tab).replace("@DEBUG@" + chr(10), dbg).replace("@DEBUG2@" + chr(10), dbg2).replace("@DEBUG3@" + chr(10), dbg3)
                           .replace("@KILL@" + chr(10), kill_src), SYM)
    end = CAVE + 4 * len(words)
    if end > CAVE_END:
        sys.exit("routines too long: end 0x%08X" % end)

    base_lines = [x for x in (base / "SLPM-66675_F266B00B.pnach").read_text().splitlines() if x.strip()]
    used = set()
    for ln in base_lines:
        if ln.startswith("patch="):
            used.add(int(ln.split(",")[2], 16) & 0x01FFFFFF)
    lines = list(base_lines)
    lines.append("comment=Lane N: a hero at 0 HP goes down like a friend; Game Over only when both heroes are down.")
    listing = ["Lane N words (base: %s; recovery time %.0f/60 s)" % (base.name, secs60), ""]
    for i, w in enumerate(words):
        a = CAVE + 4 * i
        if a in used:
            sys.exit("CLASH with the base patch at 0x%08X" % a)
        lines.append("patch=1,EE,%08X,word,%08X" % (a, w))
        for k in [k for k, v in syms.items() if v == a and k not in SYM]:
            listing.append("%s:" % k)
        listing.append("  %08X  %08X  %s" % (a, w, mips.dis(w, a)))
    listing.append("")
    for addr, orig, label, what, kind in HOOKS:
        have = elf.word(addr)
        if have != orig:
            sys.exit("hook 0x%08X: expected %08X in the game program, found %08X" % (addr, orig, have))
        if addr in used:
            sys.exit("CLASH with the base patch at hook 0x%08X" % addr)
        if label in skip:
            listing.append("hook %08X (%s): NOT installed in this variant" % (addr, what))
            continue
        word = syms[label] if kind == "table" else ((3 << 26) | ((syms[label] >> 2) & 0x3FFFFFF))
        lines.append("patch=1,EE,%08X,word,%08X" % (addr, word))
        listing.append("hook %08X: was %08X, now %08X (%s%s) -- %s" % (
            addr, orig, word, "jal " if kind == "jal" else "", label, what))
    if extra:
        lines.append("comment=TEST-ONLY lines follow (never part of the game patch).")
        lines += extra
        listing.append("")
        listing.append("TEST-ONLY lines appended: %d" % len(extra))
    out.mkdir(parents=True, exist_ok=True)
    (out / "SLPM-66675_F266B00B.pnach").write_text(chr(10).join(lines) + chr(10))
    listing.append("")
    listing.append("cave used: 0x%08X-0x%08X (%d words); variables 0x%08X-0x%08X" % (
        CAVE, end - 1, len(words), SYM["N_VARS"], SYM["N_VARS"] + 0x1F))
    (out / "listing.txt").write_text(chr(10).join(listing) + chr(10))
    print(out, "base lines", len(base_lines), "+ lane N", len(lines) - len(base_lines), "| cave end 0x%08X" % end)


if __name__ == "__main__":
    main()
