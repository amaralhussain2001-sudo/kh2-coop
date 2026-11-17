"""Lane E: the "both heroes at the exit" rule (used by make_e.py with the option 'exit' or 'exit1').

Background (VERIFIED by decompiling and tests, see docs/lanes/E-identity.md):
  * Every frame the task 0x00182C60 takes the position of ONE object, the "trigger owner" 0x0034ED04 (set by the
    game's attach routine, so it is player 1's hero with the identity rule), and offers it to every area event of
    the room (table 0x01C60588, 12 bytes each, count 0x0034ED00) by calling 0x00182980 (call at 0x00182D04).
  * 0x0019A048 walks the area event's trigger volumes and asks each one "is this point inside?" (virtual method
    at +8, called at 0x0019A168). If yes it runs the area event (0x0019A1A0): kind 1 = jump to another room,
    kind 3 = start an event, others = spawn ambushes, map visibility, etc.
  * A door also wants the engine's player to be walking into it (0x001DB198 / 0x0019A6C0 look at 0x0034E948).

Rule added here, for kind 1 (room exit) and kind 3 (event trigger) only:
  1. A volume counts as entered only when the OTHER hero is inside the SAME volume too.
  2. ('exit', default) the area event is offered a second time with the twin as the walking hero, so it does not
     matter which of the two walks into the door last. During that second offer the engine's player pointer is the
     twin and is put back right after. ('exit1' = rule 1 only: player 1's hero must be the one walking in.)
If there is no twin in the room nothing changes. Other kinds still follow player 1's hero only.
"""
from asm import assemble

INSIDE = """
e_inside:                         # hook 0x0019A168 (was: jalr v0). a0 = volume, a1 = point, v0 = method, s1 = area event
    addiu sp,sp,-32
    sd ra,0(sp)
    sd v0,8(sp)
    jalr v0                       # is the walking hero inside?
    nop
    beq v0,zero,e_in_out
    nop
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)        # 1 during the second offer (twin walking)
    lw t3,8(s1)
    lbu t6,0(t3)                  # kind of area event
    addiu t5,t6,-1
    beq t5,zero,e_in_both         # 1 = jump to another room
    addiu t5,t6,-3
    beq t5,zero,e_in_both         # 3 = start an event
    nop
    beq t4,zero,e_in_out          # other kinds: first offer as before ...
    nop
    b e_in_out                    # ... and never on the second offer
    move v0,zero
e_in_both:
    lw a0,%lo(V_TWIN)(t7)         # the other hero: the twin on the first offer ...
    beq t4,zero,e_in_other
    nop
    lw a0,%lo(V_P1)(t7)           # ... player 1's hero on the second
e_in_other:
    beq a0,zero,e_in_out          # no twin here: as before
    nop
    jal POS_OF                    # game: pointer to an object's position
    nop
    move a1,v0
    ld t9,8(sp)
    jalr t9                       # is the other hero inside the same volume?
    move a0,s0
e_in_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""

SECOND_OFFER = """
e_offer:                          # hook 0x00182D04 (was: jal 0x00182980). a0 = area event table entry, a1 = point
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal AREA_OFFER                # first offer: player 1's hero, as the game does
    nop
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    beq t6,zero,e_of_done         # no twin
    nop
    ld a0,8(sp)
    lw t5,4(a0)
    andi t5,t5,1
    bne t5,zero,e_of_done         # this entry is switched off
    nop
    lw t0,8(a0)                   # the area event
    beq t0,zero,e_of_done
    nop
    lw t1,8(t0)
    lbu t2,0(t1)                  # its kind
    addiu t3,t2,-1
    beq t3,zero,e_of_go
    addiu t3,t2,-3
    bne t3,zero,e_of_done         # only exits (1) and event triggers (3) get the second offer
    nop
e_of_go:
    lui t5,%hi(G_PLAYER)
    lw t4,%lo(G_PLAYER)(t5)
    beq t4,zero,e_of_done
    nop
    beq t4,t6,e_of_done           # the twin is the engine's player (should not happen): leave it
    nop
    sw t4,%lo(V_P1)(t7)
    sw t6,%lo(G_PLAYER)(t5)       # the engine's player = the twin, only during the second offer
    li t3,1
    sw t3,%lo(V_PASS2)(t7)
    lw t3,4(t0)
    andi t3,t3,0x18               # what the first offer found (inside / door-approach flags)
    sd t3,16(sp)
    sd t0,24(sp)
    jal POS_OF
    move a0,t6
    move a1,v0
    jal AREA_OFFER                # second offer: the twin as the walking hero
    ld a0,8(sp)
    lui t7,%hi(V_TWIN)
    sw zero,%lo(V_PASS2)(t7)
    lw t4,%lo(V_P1)(t7)
    lui t5,%hi(G_PLAYER)
    sw t4,%lo(G_PLAYER)(t5)       # put the engine's player back
    ld t0,24(sp)
    ld t3,16(sp)
    lw t2,4(t0)
    or t2,t2,t3
    sw t2,4(t0)                   # keep the first offer's flags
e_of_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""


def add(code, hooks, notes, sym, opts):
    base = 0x000F0420
    s = dict(sym)
    s["POS_OF"] = 0x0016C028
    s["AREA_OFFER"] = 0x00182980
    s["V_PASS2"] = 0x000F05D0
    s["V_P1"] = 0x000F05D4
    text = INSIDE + ("" if "exit1" in opts else SECOND_OFFER)
    words, syms = assemble(base, text, s)
    for i, w in enumerate(words):
        code[base + 4 * i] = w
    end = base + 4 * len(words) - 1
    if end >= 0x000F05C0:
        raise SystemExit("exit routines run into the variables")
    hooks[0x0019A168] = (3 << 26) | ((syms["e_inside"] >> 2) & 0x3FFFFFF)     # was: jalr v0 (0x0040F809)
    if "exit1" not in opts:
        hooks[0x00182D04] = (3 << 26) | ((syms["e_offer"] >> 2) & 0x3FFFFFF)  # was: jal 0x00182980
    notes.append("exit rule (both heroes%s): routines 0x%08X-0x%08X" % (
        ", player 1 walks in" if "exit1" in opts else ", either walks in", base, end))
