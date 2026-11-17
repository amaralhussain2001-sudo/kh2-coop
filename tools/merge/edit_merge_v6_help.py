"""One-off: tools/merge/merge_v6.py, THIRTEENTH GLUE: one helper goes with each hero when the heroes split up
(the user's rule in KH2-COOP-PLAN.md). Option --no-helpers leaves it out."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "HELP_SRC" in t:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (t.count(old), old[:70])
    t = t.replace(old, new)


DOC = '''THIRTEENTH GLUE: WHEN THE HEROES SPLIT UP, ONE HELPER GOES WITH EACH (option --no-helpers leaves it out).
What was there: Donald, Goofy and the world's guest follow player 1's hero only. Found on 2026-11-11 in a quiet
room with helpers (disc test-s1-hb9f): the helpers are led by the game's own "follow" system (program
0x0010A000-0x0011C400), not by their scripts. Three tasks run it every step: 0x00111F50 (rebuilds the member
table 0x00341708 = leader, helper, helper; the leader is the engine's player, read at 0x00111E98; records the
leader's trail of steps at 0x003A9040; sets the places beside the leader; runs each helper's own update),
0x001122A0 and 0x00112388 (each helper's later updates). Proof: with the read at 0x00111E98 turned to the twin,
both helpers walked to the twin (test w-test-lead0); nine pointers to "the player" held on the twin changed
nothing; the old bit search never tried that read because it had index 0.
The glue: the three task routines are replaced by wrappers (the words that hand their addresses to the task
list at 0x001123F4 / 0x0011241C / 0x0011243C). Each wrapper runs the game's routine for player 1's hero and the
helpers that go with him, then, when a helper goes with the twin, a second time with the twin as the leader, the
twin's helpers in the table and the follow system's leader memory swapped for a second copy (0x000F5840...:
0x00341720-0x0034177F places and steps, 0x003417B0-0x003417DF ground / target / clocks, 0x003A9040-0x003A924F
the trail). The table itself always holds the true members again when a wrapper ends, and the game's own
rebuild (hooked at 0x00111F74) sees only true changes, so the lists that follow the party (0x00135818) are told
nothing new. Who goes with whom (hp_assign, once a step): while the heroes are less than 900 units apart all
helpers go with player 1's hero as before; farther apart, the pairing with the smaller sum of (squared)
distances is taken, one helper each, and kept until the heroes are less than 550 apart again. No twin: the
game's own behaviour, word for word.

'''

SRC = '''HELP_AT = 0x000F5200
HELP_END = 0x000F5600
HELP_DATA = 0x000F5800            # +0 pass, +4 split, +8 / +C who the two helpers go with (0 player 1, 1 the twin),
#                                   +10 the true member table (3 words), +40 the second copy of the leader memory
HELP_SRC = """
hp_x:                             # swap t2 words at t0 and t1 (both move on)
    lw t3,0(t0)
    lw t4,0(t1)
    sw t4,0(t0)
    sw t3,0(t1)
    addiu t2,t2,-1
    addiu t0,t0,4
    bne t2,zero,hp_x
    addiu t1,t1,4
    jr ra
    nop
hp_swap:                          # the follow system's leader memory <-> the second copy
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t0,0x0034
    addiu t0,t0,0x1720
    lui t1,0x000F
    addiu t1,t1,0x5840
    jal hp_x
    li t2,24
    lui t0,0x0034
    addiu t0,t0,0x17B0
    jal hp_x
    li t2,12
    lui t0,0x003B
    addiu t0,t0,-28608            # 0x003A9040: the trail
    jal hp_x
    li t2,132
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
hp_table:                         # a0 = pass: the member table as that pass must see it
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0x10(t7)
    beq a0,zero,ht_l
    lui t1,0x000F
    lw t0,0x05CC(t1)              # pass 1: the leader is the twin
ht_l:
    sw t0,0(t6)
    lw t0,0x14(t7)
    lw t1,0x08(t7)
    beq t1,a0,ht_1
    nop
    move t0,zero
ht_1:
    sw t0,4(t6)
    lw t0,0x18(t7)
    lw t1,0x0C(t7)
    beq t1,a0,ht_2
    nop
    move t0,zero
ht_2:
    jr ra
    sw t0,8(t6)
hp_full:                          # the member table as the game made it
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0x10(t7)
    lw t1,0x14(t7)
    lw t2,0x18(t7)
    sw t0,0(t6)
    sw t1,4(t6)
    jr ra
    sw t2,8(t6)
hp_pass1q:                        # v0 = 1 when a helper that is there goes with the twin
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq t6,zero,pq_no
    addiu t7,t7,0x5800
    lw t0,0x08(t7)
    beq t0,zero,pq_2
    lw t1,0x14(t7)
    bne t1,zero,pq_yes
    nop
pq_2:
    lw t0,0x0C(t7)
    beq t0,zero,pq_no
    lw t1,0x18(t7)
    bne t1,zero,pq_yes
    nop
pq_no:
    jr ra
    move v0,zero
pq_yes:
    jr ra
    li v0,1
hp_d2:                            # f0 = flat squared distance of the objects a0 and a1 (0 when one is missing)
    mtc1 zero,f0
    beq a0,zero,hd_end
    nop
    beq a1,zero,hd_end
    nop
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
    lwc1 f2,0x70(a1)
    lwc1 f3,0x78(a1)
    sub.s f0,f0,f2
    sub.s f1,f1,f3
    mul.s f0,f0,f0
    mul.s f1,f1,f1
    add.s f0,f0,f1
hd_end:
    jr ra
    nop
hp_assign:                        # once a step: who goes with whom
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    lui s2,0x000F
    lw s1,0x05CC(s2)              # the twin
    addiu s2,s2,0x5800
    beq s1,zero,ha_none
    lui t5,0x0035
    lw s0,-5816(t5)               # player 1's hero
    beq s0,zero,ha_none
    move a0,s0
    jal hp_d2
    move a1,s1
    lw t0,0x04(s2)
    bne t0,zero,ha_split
    lui t1,0x4945
    ori t1,t1,0xC100              # 810000.0 = 900 * 900
    mtc1 t1,f6
    c.lt.s f6,f0
    bc1f ha_done                  # together: everybody with player 1's hero (as it is)
    nop
    li t0,1
    sw t0,0x04(s2)                # the heroes have split up
    lui t0,0x0034
    addiu t0,t0,0x1720
    lui t1,0x000F
    addiu t1,t1,0x5840
    li t2,168
ha_cp:                            # the second copy starts as a copy ...
    lw t3,0(t0)
    sw t3,0(t1)
    addiu t2,t2,-1
    addiu t1,t1,4
    beq t2,zero,ha_cpd
    addiu t0,t0,4
    li t3,144
    bne t2,t3,ha_cp2
    nop
    lui t0,0x0034
    b ha_cp
    addiu t0,t0,0x17B0
ha_cp2:
    li t3,132
    bne t2,t3,ha_cp
    nop
    lui t0,0x003B
    b ha_cp
    addiu t0,t0,-28608
ha_cpd:
    lui t1,0x000F
    addiu t1,t1,0x58D0            # ... with an empty trail (as the game's own reset 0x0010B550 leaves it)
    li t3,-1
    sw zero,0(t1)
    sw t3,4(t1)
    lui t2,0x01C6
    lw a0,0x0528(t2)              # helper 1
    jal hp_d2
    move a1,s0
    swc1 f0,32(sp)
    lui t2,0x01C6
    lw a0,0x052C(t2)              # helper 2
    jal hp_d2
    move a1,s1
    lwc1 f1,32(sp)
    add.s f0,f0,f1
    swc1 f0,32(sp)                # helper 1 with player 1 + helper 2 with the twin
    lui t2,0x01C6
    lw a0,0x0528(t2)
    jal hp_d2
    move a1,s1
    swc1 f0,36(sp)
    lui t2,0x01C6
    lw a0,0x052C(t2)
    jal hp_d2
    move a1,s0
    lwc1 f1,36(sp)
    add.s f0,f0,f1                # helper 1 with the twin + helper 2 with player 1
    lwc1 f1,32(sp)
    c.lt.s f0,f1
    li t0,1
    bc1t ha_swapd
    nop
    sw zero,0x08(s2)
    b ha_done
    sw t0,0x0C(s2)
ha_swapd:
    sw t0,0x08(s2)
    b ha_done
    sw zero,0x0C(s2)
ha_split:
    lui t1,0x4893
    ori t1,t1,0xB480              # 302500.0 = 550 * 550
    mtc1 t1,f6
    c.lt.s f0,f6
    bc1f ha_done                  # still apart: the pairing stays
    nop
ha_none:
    sw zero,0x04(s2)
    sw zero,0x08(s2)
    sw zero,0x0C(s2)
ha_done:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
hp_rebuild:                       # call at 0x00111F74 (was: jal 0x00111E50, the game's rebuild of the member table)
    lui t7,0x000F
    lw t6,0x5800(t7)
    bne t6,zero,hr_p1
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00111E50                # pass 0: the game's own rebuild (it tells the party lists about true changes)
    nop
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0(t6)
    lw t1,4(t6)
    lw t2,8(t6)
    sw t0,0x10(t7)                # remember the true table
    sw t1,0x14(t7)
    sw t2,0x18(t7)
    ld ra,0(sp)
    addiu sp,sp,16
    j hp_table                    # and hide the helpers that go with the twin
    move a0,zero
hr_p1:
    j hp_table
    li a0,1
hp_taskA:                         # task routines (their addresses are handed to the task list at 0x001123F0...)
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    jal hp_assign
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x1F50
    b hp_body
    move s1,zero
hp_taskB:
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x22A0
    b hp_body
    li s1,1
hp_taskC:
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x2388
    li s1,1
hp_body:
    beq s1,zero,hb_p0             # (the first task sets the table itself, after the game's rebuild)
    nop
    jal hp_table
    move a0,zero
hb_p0:
    jalr s0                       # for player 1's hero and his helpers
    move a0,s2
    jal hp_pass1q
    nop
    beq v0,zero,hb_end
    nop
    jal hp_swap
    nop
    lui t7,0x000F
    li t6,1
    sw t6,0x5800(t7)
    jal hp_table
    li a0,1
    jalr s0                       # for the twin and his helpers
    move a0,s2
    lui t7,0x000F
    jal hp_swap
    sw zero,0x5800(t7)
hb_end:
    jal hp_full
    nop
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
"""
# (address, word the program has, what the new word is made from, text)
HELP_HOOKS = (
    (0x00111F74, 0x0C044794, "jal:hp_rebuild", "the member table's rebuild in the first follow task"),
    (0x001123F4, 0x3C070011, "lui", "first follow task: high half of its routine's address"),
    (0x001123FC, 0x24E71F50, "lo:hp_taskA", "first follow task: low half (was 0x00111F50)"),
    (0x0011241C, 0x3C070011, "lui", "second follow task: high half"),
    (0x00112424, 0x24E722A0, "lo:hp_taskB", "second follow task: low half (was 0x001122A0)"),
    (0x0011243C, 0x3C070011, "lui", "third follow task: high half"),
    (0x00112444, 0x24E72388, "lo:hp_taskC", "third follow task: low half (was 0x00112388)"),
)

'''

GLUE = '''    if "--no-helpers" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(HELP_AT, HELP_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HELP_AT + 4 * len(code) <= HELP_END, "helper glue too long: %d words" % len(code)
        for i, w in enumerate(code):
            a = HELP_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (one helper goes with each hero when they split up)"
        n_glue += len(code)
        for a, w0, how, what in HELP_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            if how == "lui":
                w = 0x3C07000F                                      # lui a3,0x000F
            elif how.startswith("lo:"):
                lo = labels[how[3:]] & 0xFFFF
                assert labels[how[3:]] >> 16 == 0x000F and lo < 0x8000
                w = 0x24E70000 | lo                                 # addiu a3,a3,lo
            else:
                w = (3 << 26) | ((labels[how[4:]] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (helpers): " + what
            n_glue += 1

'''

rep("  python -I tools/merge/merge_v6.py [outDir]", DOC + "  python -I tools/merge/merge_v6.py [outDir]")
rep("[--no-nea", "[--no-helpers] [--no-nea")
rep("REACT_AT = 0x000F4A00", SRC + "REACT_AT = 0x000F4A00")
rep('''    if "--react" in sys.argv:          # EXPERIMENT''', GLUE + '''    if "--react" in sys.argv:          # EXPERIMENT''')
p.write_text(t, encoding="utf-8")
print("ok")
