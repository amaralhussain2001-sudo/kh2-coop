r"""One-off (STATE part 146; the user's words 2026-11-18: "finish the 11 9 8 for now", item 11 (c) = a Light Cycle rider comes back):
THE EIGHTY-THIRD GLUE, option --lcrevive. Research: local\analysis\agent-rides\rides-design.txt (read-only agent) and this part.
The Light Cycle (object 0x05F5, class table 0x003521E0, used by the Light Cycle alone; both riders, the twin's too): when a cycle's HP
reaches 0, 0x00187818 calls class +0x5C = 0x001CF4F8: 0x00179E18 (commands off, the fallen flag +0x7F8 bit 4), motion 30 (the
crash), then the mission's failure event 90 or the Game Over (0x001AF290). So the ride ended when EITHER cycle was destroyed.
Now (table words +0x5C and +0x0C):
  lc_die: with a twin, when the OTHER rider's cycle is there (class 0x003521E0) and not fallen: only the crash part (0x00179E18 and
          motion 30) and his down timer = LC_DOWN steps. Otherwise the game's 0x001CF4F8 (both destroyed: the ride ends as before;
          one hero alone: nothing changes).
  lc_tick (in front of the game's +0x0C, 0x00178758): notes the non-twin rider (V_LC1); counts a fallen rider's timer down; at 0
          he gets up the way the game's own revive (0x00179F80) does it - the fallen flag off, 0x001852B8, the action state 23 of a
          riding cycle (the cycle's init), the control word ([+0xB44]+0x9E0, only when +0xB44 is not 0), commands on
          (0x001D6AB0), HP + max (class +0x78) - then motion 44 and motion 0 queued (as the cycle's init). A rider that is not
          fallen any more (a Continue rebuilt him) loses his timer.
Without --lcrevive the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_lcrevive.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--lcrevive" in t:
    raise SystemExit("already done")

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTY-THIRD GLUE (built only with the option --lcrevive): A DESTROYED LIGHT CYCLE COMES BACK. The Light Cycle's class table
(0x003521E0, Light Cycle only): +0x5C (HP 0; the game's 0x001CF4F8 ends the ride) -> lc_die: while the other rider's cycle is up,
only the crash part (0x00179E18, motion 30) and a down timer (LC_DOWN steps); both destroyed, or no twin: the game's own end.
+0x0C (the cycle's step, 0x00178758) -> lc_tick: notes the non-twin rider (V_LC1 0x000DE820), counts the timers (V_LCT1 0x000DE824,
V_LCT2 0x000DE828 the twin's) and at 0 lifts the rider like the game's revive 0x00179F80 (HP + max) back into riding (state 23,
motion 44 then 0). Room 0x000DE580 .. 0x000DE780.
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eighty-third glue (only with --lcrevive) --------------------------------------------------------------------
LC_AT = 0x000DE580
LC_END = 0x000DE780
LC_HOOKS = ((0x003521EC, 0x00178758, "lc_tick"), (0x0035223C, 0x001CF4F8, "lc_die"))   # Light Cycle class table +0x0C, +0x5C
LC_DOWN = 300                                       # steps a destroyed cycle stays down
LC_SRC = """
lc_die:                           # class +0x5C (was 0x001CF4F8), a0 = a cycle whose HP reached 0 (not fallen yet)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (his cycle)
    beq t6,zero,ld_game           # one hero: the game's end
    lui t5,0x000E
    beq a0,t6,ld_chk              # the twin's cycle: the other rider is V_LC1
    lw t4,-6112(t5)               # V_LC1 (0x000DE820)
    move t4,t6                    # player 1's cycle: the other rider is the twin
ld_chk:
    beq t4,zero,ld_game
    nop
    beq t4,a0,ld_game
    lui t3,0x0035
    ori t3,t3,0x21E0              # the Light Cycle's class
    lw t2,0(t4)
    bne t2,t3,ld_game             # the other rider is not on a cycle
    nop
    lw t2,0x7F8(t4)
    andi t2,t2,4
    bne t2,zero,ld_game           # the other rider is down too: the ride ends (the game's way)
    nop
    addiu sp,sp,-16               # one rider down: the crash, and his timer
    sd s0,0(sp)
    sd ra,8(sp)
    jal 0x00179E18                # commands off, the fallen flag
    move s0,a0
    .word 0x44806000              # mtc1 zero,f12
    .word 0x44806800              # mtc1 zero,f13
    addiu a0,s0,320
    jal 0x0017F488                # motion 30 (the crash), as 0x001CF4F8
    addiu a1,zero,30
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lui t5,0x000E
    addiu t4,zero,LC_DOWN
    bne s0,t6,ld_p1
    nop
    b ld_done
    sw t4,-6104(t5)               # V_LCT2 (0x000DE828): the twin's timer
ld_p1:
    sw t4,-6108(t5)               # V_LCT1 (0x000DE824)
ld_done:
    ld s0,0(sp)
    ld ra,8(sp)
    jr ra
    addiu sp,sp,16
ld_game:
    j 0x001CF4F8
    nop
lc_tick:                          # class +0x0C (was 0x00178758), a0 = a cycle, every step
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq t6,zero,lt_game           # one hero: as the game
    lui t5,0x000E
    beq a0,t6,lt_tw
    addiu t3,t5,-6104             # &V_LCT2 (the twin's timer)
    sw a0,-6112(t5)               # V_LC1 = this (non-twin) rider
    addiu t3,t5,-6108             # &V_LCT1
lt_tw:
    lw t2,0(t3)                   # his down timer
    beq t2,zero,lt_game
    lw t1,0x7F8(a0)
    andi t1,t1,4
    beq t1,zero,lt_clear          # not fallen (rebuilt by a Continue): forget the timer
    addiu t2,t2,-1
    bne t2,zero,lt_game
    sw t2,0(t3)
    addiu sp,sp,-16               # the time is up: he gets up
    sd s0,0(sp)
    sd ra,8(sp)
    move s0,a0
    lw t7,0x7F8(s0)
    addiu t6,zero,-5
    and t7,t7,t6
    jal 0x001852B8                # (as the game's 0x00179F10)
    sw t7,0x7F8(s0)               # the fallen flag off
    move a0,s0
    jal 0x0016BD60                # the action state of a riding cycle (its init)
    addiu a1,zero,23
    lw t7,0xB44(s0)
    beq t7,zero,lt_nocw           # (0x00179F10 writes the control word; never through a 0 pointer)
    nop
    sw s0,0x9E0(t7)
lt_nocw:
    jal 0x001D6AB0                # commands on
    lw a0,0xB3C(s0)
    lw t7,0x48C(s0)               # the unit slot
    beq t7,zero,lt_mot
    move a0,s0
    lw t6,0(s0)
    lw a1,4(t7)                   # its maximum HP
    lw v0,0x78(t6)                # class +0x78: HP + a1 (as the game's revive 0x00179F80)
    move a2,zero
    jalr v0
    move a3,zero
lt_mot:
    .word 0x44806000              # mtc1 zero,f12
    .word 0x44806800              # mtc1 zero,f13
    addiu a0,s0,320
    jal 0x0017F488                # motion 44, as the cycle's init
    addiu a1,zero,44
    .word 0x44806000
    .word 0x44806800
    addiu a0,s0,320
    move a1,zero
    jal 0x0017F5E0                # then motion 0, queued
    move a2,zero
    move a0,s0
    ld s0,0(sp)
    ld ra,8(sp)
    j 0x00178758
    addiu sp,sp,16
lt_clear:
    sw zero,0(t3)
lt_game:
    j 0x00178758
    nop
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--lcrevive" in sys.argv:                                           # eighty-third glue (a destroyed Light Cycle comes back)
        code, labels = assemble(LC_AT, LC_SRC.replace("LC_DOWN", str(LC_DOWN)), {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert LC_AT + 4 * len(code) <= LC_END, "the eighty-third glue does not fit"
        clash = [a for a in words if LC_AT <= a < LC_END or 0x000DE820 <= a < 0x000DE82C]
        assert not clash, "patch words in the eighty-third glue's room: %08X" % clash[0]
        for i, w in enumerate(code):
            a = LC_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (a destroyed Light Cycle comes back)"
        for a, w0, label in LC_HOOKS:
            hook_game(a, w0, labels[label], "the Light Cycle's class table: " + label)
        n_glue += len(code) + 2

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-third glue (--lcrevive) added")
