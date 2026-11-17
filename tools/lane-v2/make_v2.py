"""Lane V2 patch generator (CRC F266B00B): merged build v2 + this lane's HUD sections.

  python -I tools/lane-v2/make_v2.py <outDir> [section ...]

Sections of this lane (give the names you want; none = only the merged-v2 base):
  marker    '1P' / '2P' markers over the heroes (needs p2gauge)
  views     base = merged-v2 + lane V1's two views (snapshot v1_views.py) instead of merged-v2 alone
  perview   two-view mode: each player's own HUD in that player's view picture (needs views and p2gauge)
  p2gauge   interim gauge for player 2 on the ONE-view HUD: a third "friend style" gauge (face, HP ring, MP bar)
            bound to the twin's own unit slot, stacked above the friend gauges.
The merged-v2 lines come from tools/merge/make_all.py (imported, not edited): build(v2=True, without base).
Writes SLPM-66675_F266B00B.pnach and listing.txt into <outDir>.
Code cave of this lane: 0x000F7000-0x000F7FFF (variables from 0x000F7F00 up; they rely on zero memory at boot).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import make_all as M  # noqa: E402
import mips  # noqa: E402

SYM = dict(M.SYM)
SYM.update({
    # game routines (2D layer / HUD)
    "GAUGE_F_CTOR": 0x0031B3B8,   # friend gauge constructor (object of 0x15B0 bytes)
    "GAUGE_F_INIT8": 0x00154F38,  # friend gauge set-up (0x00154F30) entered after its first two instructions
    "GAUGE_F_REFRESH": 0x00155300,  # friend gauge: take the character from party slot index+1, face, HP cache
    "GAUGE_F_UPD_TAIL": 0x00155704,  # friend gauge update, after its "party changed" check
    "GAUGE_SHOWHIDE": 0x001582A8,  # show or hide a gauge's object group by whether it has a character
    "GAUGE_KIND": 0x001581F8,     # gauge+0x18 = state of its character (normal / danger)
    "GRP_NODRAW": 0x001398D0,     # every 2D object of group a0: flag 0x02 (not drawn)
    "GRP_NOUPD": 0x00139B28,      # every 2D object of group a0: flag 0x100 (gauge not updated)
    "GRP_DRAW": 0x00139858,       # clear flag 0x02
    "GRP_UPD": 0x00139BA0,        # clear flag 0x100
    "HUD_PAUSE": 0x0013DB60,      # gauges off (groups 3-6)
    # game data
    "MGR_CUR": 0x00347F80,        # current 2D layer manager
    "PARTY": 0x00348638,          # HUD party table: 3 objects, then 3 flag words
    # this lane's variables
    "V_TG": 0x000F7F00,           # the twin gauge object (0 if the HUD does not exist)
    "V_TGH": 0x000F7F04,          # height of one gauge row (taken from the game's own set-up)
    # per-view HUD
    "SET_VIEW": 0x001069F8,       # choose the current view index
    "VIEW_INDEX": 0x0033CC40,     # current view index (0 = camera 1 / player 1, 1 = camera 2 / player 2)
    "HUD_MATRIX": 0x00139C90,     # current 2D layer manager: world -> screen matrix from the current view
    "SCHED_RUN": 0x001029E8,      # run a task scheduler
    "BUF_SWITCH": 0x0014E0D8,     # two-view mode: the first view picture is finished (task at priority 90000)
    "MGR0": 0x00347EA0,           # 2D layer manager 0 = the field HUD
    "MGR_END": 0x00139DC0,        # what the HUD task's end routine calls
    "GAUGE_P_CTOR": 0x0031B130,   # player gauge constructor (object of 0x3D00 bytes)
    "GAUGE_P_REFRESH": 0x00156E48,  # player gauge: take the character from party slot 0, face, cached values
    "CMD_DISPLAY": 0x003484A0,    # pointer to the command menu display object (its control object at +0x29C)
})
O_LIVE, O_DREW, O_PMODE, O_NTH, O_TG2, O_PG, O_PGT = 0x7F08, 0x7F0C, 0x7F14, 0x7F18, 0x7F1C, 0x7F20, 0x7F24   # offsets from 0x000F0000
O_MK1, O_MK2, O_MKK = 0x7F28, 0x7F2C, 0x7F30
MK_STEPS = 1                      # animation steps a marker takes when it is made (it then stays like that)
MK_GROUP = 0x35                   # 2D object group id of the 1P / 2P markers
MK_DY = 0xC32A                    # upper half of the float -170.0: how far above a hero's position its marker floats
PG_GROUP = 0x32                   # 2D object group id of player 2's own big gauge (0x31 = small gauge of player 1's hero)
O_VON = 0x6F04                    # lane V1: 1 while the two-view draw tasks in the scene are lane V1's
TG_GROUP = 0x30                   # 2D object group id of the twin gauge (the game uses 3-6 for its gauges)
TG_A3 = TG_GROUP - 3 - 2          # "group base" so that base + index(2) + 3 = TG_GROUP

FACE_SCALE = 0x3F000000           # 0.5 as a float (only the upper 16 bits are used)

P2GAUGE_AT = 0x000F7000
P2GAUGE_SRC = """
tg_class:                         # class table of the twin gauge: the friend gauge's (0x0034A848) with our update
    .word 0x001391E8
    .word tg_update
    .word 0x001391F8
    .word 0x0031D0F8
    .word 0x0031D1B8
    .word 0x00139510
    .word 0x00155300
    .word 0x00155460
    .word 0x00155478
    .word 0x00155490
    .word 0x001554A8
    .word 0

tg_create:                        # hook 0x0013D9D8: end of the HUD's gauge creation (frame already released)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui t7,%hi(MGR_CUR)
    lw t7,%lo(MGR_CUR)(t7)
    lw a0,0x14(t7)                # the layer's owner: its allocator
    lw t6,0(a0)
    lw v0,0(t6)
    li a1,0x15B0                  # size of a friend gauge
    jalr v0
    move a2,zero
    move s0,v0
    jal GAUGE_F_CTOR
    move a0,v0
    lui t6,%hi(tg_class)
    addiu t6,t6,%lo(tg_class)
    sw t6,0(s0)                   # our class table
    lui t7,%hi(V_TG)
    sw s0,%lo(V_TG)(t7)
    move a0,s0
    move a1,zero                  # no character yet: the first update takes the twin
    jal tg_f30
    li a2,2                       # index 2 = third row of the stack
    sw zero,0x380(s0)             # face picture slot 0: the twin has the same face picture as player 1's hero,
                                  # so both use the one already loaded (slot 3 would lie outside the face area)
    lw t6,0x508(s0)               # the set-up placed it at row height * 2
    sra t6,t6,1
    lui t7,%hi(V_TGH)
    sw t6,%lo(V_TGH)(t7)          # remember the height of one row
    ld ra,0(sp)
    ld s0,8(sp)
    j HUD_PAUSE                   # what the game did here (through tg_pause for our group too)
    addiu sp,sp,32

tg_f30:                           # the game's friend gauge set-up with our own group base instead of 1
    addiu sp,sp,-112
    j GAUGE_F_INIT8
    li a3,TG_A3

tg_update:                        # class method "update" of the twin gauge. a0 = gauge
    addiu sp,sp,-16
    sd s0,0(sp)
    sd ra,8(sp)
    move s0,a0
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    lw t5,0x34(s0)
    beq t6,t5,tg_same             # same twin as last time (or still none)
    nop
    jal GAUGE_F_REFRESH           # character = party slot 3 = the twin (tg_party); face; HP cache
    move a0,s0
    jal GAUGE_SHOWHIDE            # show the gauge when there is a twin, hide it when there is none
    move a0,s0
tg_same:
    lw t6,0x110(s0)               # the face object's sequence flags: bit 1 = use our scale
    ori t6,t6,2
    sw t6,0x110(s0)
    lui t6,FACE_SCALE_HI          # the hero's face picture is twice the size of a friend's: draw it at half size
    sw t6,0x190(s0)               # sequence scale: x factor (the overall factor at +0x18C is the game's own)
    sw t6,0x194(s0)               # y factor
    jal tg_place
    move a0,s0
    jal GAUGE_KIND
    move a0,s0
    j GAUGE_F_UPD_TAIL            # the rest of the game's friend gauge update (same stack frame layout)
    nop

tg_place:                         # row of the stack = number of friends present. a0 = gauge
    lui t7,%hi(PARTY)
    addiu t7,t7,%lo(PARTY)
    lw t6,4(t7)                   # party slot 1
    lw t5,8(t7)                   # party slot 2
    sltu t6,zero,t6
    sltu t5,zero,t5
    addu t6,t6,t5
    lui t7,%hi(V_TGH)
    lw t3,%lo(V_TGH)(t7)
    move t4,zero
    beq t6,zero,tg_pl_set
    li t5,1
    beq t6,t5,tg_pl_set
    move t4,t3
    addu t4,t3,t3
tg_pl_set:
    sw zero,0x504(a0)             # root sequence of the gauge: offset x
    jr ra
    sw t4,0x508(a0)               # offset y = row height * row

tg_party:                         # hook 0x0013DDA0: HUD party table getter. Slot 3 = the twin
    li t6,3
    bne a0,t6,tg_pa_norm
    lui t7,%hi(PARTY)
    lui t6,%hi(V_TWIN)
    jr ra
    lw v0,%lo(V_TWIN)(t6)
tg_pa_norm:
    addiu t7,t7,%lo(PARTY)
    sll t6,a0,2
    addu t7,t7,t6
    jr ra
    lw v0,0(t7)

tg_destroy:                       # hook 0x0013D9E0: the HUD's gauges are destroyed
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,%hi(V_TG)
    lw a0,%lo(V_TG)(t7)
    beq a0,zero,tg_de_done
    sw zero,%lo(V_TG)(t7)
    lw t6,0(a0)
    lw t7,0x10(t6)                # class method 4: destroy and free, as the game does for its gauges
    jalr t7
    nop
tg_de_done:
    ld ra,0(sp)
    addiu sp,sp,16
    addiu sp,sp,-16               # the two instructions that sat at 0x0013D9E0
    j 0x0013D9E8
    sd s0,0(sp)

tg_pause:                         # hook 0x0013DBA8: tail of "gauges off". a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    jal GRP_NOUPD                 # group 6, as the game did
    nop
    jal GRP_NODRAW
    li a0,TG_GROUP
    ld ra,0(sp)
    li a0,TG_GROUP
    j GRP_NOUPD
    addiu sp,sp,16

tg_resume:                        # hook 0x0013DB50: tail of "gauges on". a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    jal GRP_UPD                   # group 6, as the game did
    nop
    jal GRP_DRAW
    li a0,TG_GROUP
    ld ra,0(sp)
    li a0,TG_GROUP
    j GRP_UPD
    addiu sp,sp,16
"""


MARKER_AT = 0x000F7240
MARKER_SRC = """
mk_class:                         # class table of a marker: the game's "number in the scene" class (0x0034AB80) with our update
    .word 0x0015B4C0
    .word mk_update
    .word 0x0015B5D8
    .word 0x0031D9B8
    .word 0x0031DA48
    .word 0x00139510
    .word 0x001390E8
    .word 0

mk_create:                        # make both markers, if the marks' container exists (it does not yet when the gauges are made)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x0035
    lw t6,-31072(t7)              # 0x003486A0: the container of the marks over the scene
    beq t6,zero,mk_c_out          # not there: no markers in this scene
    nop
    jal mk_make
    li a0,1
    lui t7,0x000F
    sw v0,{O_MK1}(t7)
    jal mk_make
    li a0,2
    lui t7,0x000F
    sw v0,{O_MK2}(t7)
mk_c_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

mk_make:                          # a0 = number to show. Out: v0 = the new marker (built like the game's own number mark, 0x0015B680)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    jal 0x001050C8                # the heap the game takes these marks from
    move s1,a0
    move a1,v0
    jal 0x001063C0                # allocate
    li a0,0xB40
    move s0,v0
    sw zero,12(s0)
    lui t6,0x0034
    ori t6,t6,0x7E60
    sw t6,0(s0)
    jal 0x00239700                # empty sequence (the letter)
    addiu a0,s0,0x18
    sw zero,0x1B0(s0)
    lui t6,%hi(mk_class)
    addiu t6,t6,%lo(mk_class)
    sw t6,0(s0)
    addiu s2,s0,0x1B8
mk_m_loop:
    jal 0x00239700                # seven empty sequences (the digits)
    move a0,s2
    addiu s2,s2,0x158
    addiu t6,s0,0xB20
    bne s2,t6,mk_m_loop
    nop
    jal 0x0013E678                # the marks' container (their pictures)
    nop
    move a0,s0
    li a1,0x10                    # sequence 0x10: the letter after the number
    move a2,v0
    jal 0x0015B368                # set up letter and digits; registers the object (group 0xF)
    move a3,s1
    li t6,{MK_GROUP}
    sw t6,16(s0)                  # our own group
    lui t7,0x000F
    lw s2,{O_MKK}(t7)             # test knob (0 in normal use): number of animation steps to take now
    bne s2,zero,mk_m_k
    nop
    li s2,{MK_STEPS}
mk_m_k:
    jal 0x0015B578                # the game's own update of this mark = one animation step; ours never steps again,
    move a0,s0                    # so the mark stays as it looks at this moment of its animation
    addiu s2,s2,-1
    bgtz s2,mk_m_k
    nop
    move v0,s0
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,32

mk_update:                        # class method "update". a0 = marker. No animation step: the mark stays as created
    lui t7,0x000F
    lw t6,{O_MK2}(t7)
    lui t5,%hi(PARTY)
    lw t4,%lo(PARTY)(t5)          # marker 1 follows player 1's hero
    lui t5,%hi(V_TWIN)
    lw t3,%lo(V_TWIN)(t5)
    bne a0,t6,mk_u_who
    nop
    move t4,t3                    # marker 2 follows the twin
mk_u_who:
    beq t3,zero,mk_u_hide         # no twin: one hero, no markers (original picture)
    nop
    beq t4,zero,mk_u_hide
    lui t5,0x0035
    lw t5,-31072(t5)
    beq t5,zero,mk_u_hide         # the marks' container is gone
    nop
    lw t6,12(a0)
    li t5,-65
    and t6,t6,t5                  # shown (clear flag 0x40)
    sw t6,12(a0)
    lwc1 f0,0x70(t4)              # the hero's position ...
    swc1 f0,0x1A0(a0)
    lwc1 f0,0x74(t4)
    lui t6,{MK_DY}
    mtc1 t6,f1
    add.s f0,f0,f1                # ... and a fixed distance above it
    swc1 f0,0x1A4(a0)
    lwc1 f0,0x78(t4)
    swc1 f0,0x1A8(a0)
    lui t6,0x3F80
    sw t6,0x1AC(a0)
    addiu sp,sp,-16
    sd ra,0(sp)
    sd s0,8(sp)
    move s0,a0
    lui a1,%hi(MGR_CUR)
    lw a1,%lo(MGR_CUR)(a1)
    addiu a0,s0,0x1A0
    jal 0x0013A178                # scene point -> screen, with the HUD matrix of the camera of this run
    addiu a1,a1,0x20
    lw t6,0(v0)
    sw t6,0x170(s0)
    lw t6,4(v0)
    sw t6,0x174(s0)
    lw t6,8(v0)
    sw t6,0x1B0(s0)
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,16
mk_u_hide:
    lw t6,12(a0)
    ori t6,t6,0x40
    jr ra
    sw t6,12(a0)

mk_destroy:                       # hook 0x0013D9E0 (HUD gauges destroyed), before tg_destroy
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000F
    lw a0,{O_MK1}(t7)
    beq a0,zero,mk_d_2
    sw zero,{O_MK1}(t7)
    lw t6,0(a0)
    lw t7,0x10(t6)                # class method 4: destroy and free
    jalr t7
    nop
mk_d_2:
    lui t7,0x000F
    lw a0,{O_MK2}(t7)
    beq a0,zero,mk_d_3
    sw zero,{O_MK2}(t7)
    lw t6,0(a0)
    lw t7,0x10(t6)
    jalr t7
    nop
mk_d_3:
    ld ra,0(sp)
    j tg_destroy
    addiu sp,sp,16

mk_pause:                         # hook 0x0013DBA8 (tail of "gauges off"), before tg_pause. a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    jal GRP_NODRAW                # the markers go away with the gauges
    li a0,{MK_GROUP}
    ld ra,0(sp)
    li a0,6
    j tg_pause
    addiu sp,sp,16

mk_resume:                        # hook 0x0013DB50 (tail of "gauges on"), before tg_resume. a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000F
    lw t6,{O_MK1}(t7)
    bne t6,zero,mk_r_have
    nop
    jal mk_create                 # first "gauges on" of this HUD: make the markers now
    nop
mk_r_have:
    jal GRP_DRAW
    li a0,{MK_GROUP}
    ld ra,0(sp)
    li a0,6
    j tg_resume
    addiu sp,sp,16
"""

PERVIEW_AT = 0x000F7500
PERVIEW_SRC = """
pv_first:                         # hook 0x00161A40: two-view task at priority 90000 (the first view picture is complete)
    lui t7,0x000F
    lw t6,{O_VON}(t7)
    beq t6,zero,pv_f_go           # not lane V1's two views (the game's own cross-fade): untouched
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal pv_hud                    # what is drawn here lands in picture B = PLAYER 1's view (VERIFIED v2-p3-poke, v2-p4-poke)
    move a0,zero
    ld ra,0(sp)
    addiu sp,sp,16
pv_f_go:
    j BUF_SWITCH                  # what the task did
    nop

pv_second:                        # hook 0x00161C70: two-view task at priority 90130 (second picture complete; compose)
    lui t7,0x000F
    lw t6,{O_VON}(t7)
    beq t6,zero,pv_s_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal pv_hud                    # what is drawn here lands in picture A = PLAYER 2's view
    li a0,1
    ld ra,0(sp)
    addiu sp,sp,16
pv_s_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x00161C70
    j 0x00161C78
    sd ra,0(sp)

pv_hud:                           # DRAW THE COMPLETE FIELD HUD OF ONE PLAYER INTO THE CURRENT PICTURE. a0 = 0 player 1, 1 player 2
    addiu sp,sp,-48               # Call it when that player's view is complete. Full size; the picture is whatever is being drawn.
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    lui s2,0x000F
    lw s0,{O_LIVE}(s2)
    beq s0,zero,pv_h_out          # no field HUD in this scene (its task did not run in the last step)
    move s1,a0
    lui t7,%hi(VIEW_INDEX)
    lw t6,%lo(VIEW_INDEX)(t7)
    sw t6,32(sp)                  # the view index to put back
    sw s1,%lo(VIEW_INDEX)(t7)     # this player's camera
    lui t7,%hi(MGR_CUR)
    sw s0,%lo(MGR_CUR)(t7)
    addiu t6,s1,1
    sw t6,{O_PMODE}(s2)           # 1 = player 1's picture, 2 = player 2's picture
    lui t7,%hi(CMD_DISPLAY)
    lw t6,%lo(CMD_DISPLAY)(t7)    # the command menu on screen
    sw zero,36(sp)
    beq t6,zero,pv_h_run
    nop
    lw t5,0x29C(t6)               # the control object it shows (player 1's)
    beq s1,zero,pv_h_run
    sw t5,36(sp)
    lui t4,0x000F
    ori t4,t4,0x1000              # S2 = player 2's control object (lane G)
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1260              # a built control object starts with this class table
    bne t3,t2,pv_h_run            # S2 is not built: leave the menu alone
    nop
    sw t4,0x29C(t6)               # player 2's picture: the menu shows S2
pv_h_run:
    jal HUD_MATRIX                # the HUD's world -> screen matrix from this player's camera
    nop
    sw zero,16(s0)                # what the HUD task does: every object's update (see pv_ufilter), then every draw (pv_filter)
    sw zero,12(s0)
    jal SCHED_RUN
    lw a0,0(s0)
    lw t6,{O_NTH}(s2)
    addiu t6,t6,1
    sw t6,{O_NTH}(s2)             # shared objects are updated only in the first run of a step
    sw s0,{O_DREW}(s2)            # the HUD task at priority 100000 has nothing left to do in this step
    sw zero,{O_PMODE}(s2)
    lw t5,36(sp)
    beq t5,zero,pv_h_view
    lui t7,%hi(CMD_DISPLAY)
    lw t6,%lo(CMD_DISPLAY)(t7)
    beq t6,zero,pv_h_view
    nop
    sw t5,0x29C(t6)               # the menu shows player 1's control object again
pv_h_view:
    lw t6,32(sp)
    lui t7,%hi(VIEW_INDEX)
    sw t6,%lo(VIEW_INDEX)(t7)
pv_h_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48

pv_mgr:                           # hook 0x00139390: the 2D layer manager's scene task. a0 = task
    lw t6,4(a0)                   # its manager
    lui t4,%hi(MGR0)
    addiu t4,t4,%lo(MGR0)
    bne t6,t4,pv_m_go             # not the field HUD (the menu layer): untouched
    lui t7,0x000F
    lw t5,{O_DREW}(t7)
    sw zero,{O_DREW}(t7)
    sw zero,{O_NTH}(t7)
    sw zero,{O_PMODE}(t7)
    sw t6,{O_LIVE}(t7)            # the field HUD is alive in this scene
    beq t5,t6,pv_m_skip           # it was updated and drawn into the view pictures in this step
    nop
pv_m_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x00139390
    j 0x00139398
    lui t7,0x34
pv_m_skip:
    jr ra
    nop

pv_end:                           # hook 0x001393D8: the field HUD's scene task is removed (scene ends)
    lui t7,0x000F
    sw zero,{O_LIVE}(t7)
    sw zero,{O_DREW}(t7)
    sw zero,{O_NTH}(t7)
    sw zero,{O_PMODE}(t7)
    j MGR_END                     # what the end routine did (its delay slot instruction is still in place)
    nop

pv_ufilter:                       # hook 0x0013921C (HUD object's task). s0 = object, s1 = manager. Out: t7 != 0 = no update now
    lw t7,12(s0)
    andi t7,t7,0x20               # the game's own "no update" flag
    lui t4,%hi(MGR0)
    addiu t4,t4,%lo(MGR0)
    bne s1,t4,pv_uf_out           # not the field HUD
    lw t5,16(s0)                  # group id
    lui t4,0x000F
    lw t3,{O_PMODE}(t4)           # 0 = one view, 1 = player 1's picture, 2 = player 2's picture
    lw t2,0(s0)
    lw t2,4(t2)                   # the object's update routine
    lui t1,0x0014
    addiu t0,t1,-28432            # 0x001390F0: placed from a point of the scene (second part of a mark)
    beq t2,t0,pv_uf_anch
    addiu t0,t1,-7056             # 0x0013E470: mark over the scene (lock-on ring, reaction mark)
    beq t2,t0,pv_uf_anch
    lui t1,0x0016
    addiu t0,t1,-19080            # 0x0015B578: number that pops up in the scene (experience points)
    beq t2,t0,pv_uf_anch
    addiu t2,t5,-1
    sltiu t2,t2,2                 # groups 1, 2: the command menu: every run (it shows the run's player)
    bne t2,zero,pv_uf_out
    li t2,{MK_GROUP}
    beq t5,t2,pv_uf_out           # the 1P / 2P markers: every run (each camera places them; they do not animate)
    li t2,3
    beq t5,t2,pv_uf_p1            # group 3: player 1's own gauge
    li t2,0x30
    beq t5,t2,pv_uf_p1            # group 0x30: small gauge of the twin
    addiu t2,t5,-49
    sltiu t2,t2,2                 # groups 0x31, 0x32: player 2's own objects
    bne t2,zero,pv_uf_p2
    lw t2,{O_NTH}(t4)             # everything else is shared: first run of the step only
    bne t2,zero,pv_uf_skip
    nop
    b pv_uf_out
    nop
pv_uf_p1:                         # player 1's own objects: not in player 2's run
    li t2,2
    beq t3,t2,pv_uf_skip
    nop
    b pv_uf_out
    nop
pv_uf_p2:                         # player 2's own objects: only in player 2's run
    li t2,2
    beq t3,t2,pv_uf_out
    nop
pv_uf_skip:
    ori t7,t7,0x20
pv_uf_out:
    jr ra
    nop
pv_uf_anch:                       # an object placed from a point of the scene
    lw t2,{O_NTH}(t4)
    beq t2,zero,pv_uf_out         # first run of the step: its normal update (animation step and place)
    nop
    bne t7,zero,pv_uf_out
    lw t2,12(s0)
    andi t2,t2,0x100
    bne t2,zero,pv_uf_skip        # paused
    nop
    addiu sp,sp,-16               # later runs: only place it again, with the matrix of this run's camera
    sd ra,0(sp)
    addiu a0,s0,0x1A0             # its point in the scene
    jal 0x0013A178                # -> screen x, y and depth
    addiu a1,s1,0x20
    lw t6,0(v0)
    sw t6,0x170(s0)
    lw t6,4(v0)
    sw t6,0x174(s0)
    lw t6,8(v0)
    sw t6,0x1B0(s0)
    lw t6,0(s0)
    lw t6,0x18(t6)                # class method 6: apply the place (a mark's size by distance)
    jalr t6
    move a0,s0
    lw t6,0(s0)
    lui t5,0x0035
    addiu t5,t5,-31056            # 0x003486B0: a mark with a second part
    bne t6,t5,pv_uf_an2
    nop
    lw t6,0x180(s0)
    sw t6,0x340(s0)               # the second part takes the same size (as the game's update does)
pv_uf_an2:
    ld ra,0(sp)
    addiu sp,sp,16
    lw t7,12(s0)
    b pv_uf_skip
    andi t7,t7,0x20

pv_filter:                        # hook 0x0013935C (HUD draw-all). a0 = object, a1 = manager.
    lw t7,12(a0)                  # Out: t7 = flags (+ 0x02 "not drawn" if it does not belong in this picture), t6 = flags & 0x40
    lui t4,%hi(MGR0)
    addiu t4,t4,%lo(MGR0)
    bne a1,t4,pv_fi_out
    lw t5,16(a0)                  # group id
    lui t4,0x000F
    lw t3,{O_PMODE}(t4)           # 0 = one view, 1 = player 1's picture, 2 = player 2's picture
    beq t3,zero,pv_fi_p1          # one view: as player 1's picture, and both lock-on rings
    li t2,0x11
    bne t5,t2,pv_fi_grp
    li t2,2
    lui t1,%hi(V_TWIN)            # a mark of group 0x11 in a view picture: the OTHER player's lock-on ring is not drawn
    lw t0,%lo(V_TWIN)(t1)         # player 1's picture: the other player's hero = the twin
    bne t3,t2,pv_fi_lk
    nop
    lui t1,%hi(PARTY)
    lw t0,%lo(PARTY)(t1)          # player 2's picture: the other player's hero = player 1's
pv_fi_lk:
    beq t0,zero,pv_fi_out
    nop
    lw t0,0xB40(t0)               # that hero's lock-on object
    beq t0,zero,pv_fi_out
    nop
    lw t0,0x18(t0)                # its mark on the target (from the pool of world marks)
    beq t0,zero,pv_fi_out
    nop
    beq a0,t0,pv_fi_hide
    addiu t0,t0,0x1C0             # the mark's second part
    beq a0,t0,pv_fi_hide
    nop
    b pv_fi_out
    nop
pv_fi_grp:
    beq t3,t2,pv_fi_p2
    nop
pv_fi_p1:                         # player 1's picture or one view: player 2's own objects (0x31, 0x32) are not drawn
    addiu t2,t5,-49
    sltiu t2,t2,2
    bne t2,zero,pv_fi_hide
    nop
    b pv_fi_out
    nop
pv_fi_p2:                         # player 2's picture: player 1's own gauge (3) and the small twin gauge (0x30) are not drawn
    li t2,3
    beq t5,t2,pv_fi_hide
    li t2,0x30
    bne t5,t2,pv_fi_out
    nop
pv_fi_hide:
    ori t7,t7,2
pv_fi_out:
    jr ra
    andi t6,t7,0x40

tg2_class:                        # small gauge of player 1's hero (drawn in player 2's picture): friend gauge with our update
    .word 0x001391E8
    .word tg2_update
    .word 0x001391F8
    .word 0x0031D0F8
    .word 0x0031D1B8
    .word 0x00139510
    .word 0x00155300
    .word 0x00155460
    .word 0x00155478
    .word 0x00155490
    .word 0x001554A8
    .word 0

pg_class:                         # player 2's own big gauge: the player gauge's class table (0x0034A920) with our update
    .word 0x001391E8
    .word pg_update
    .word 0x001391F8
    .word 0x0031D290
    .word 0x0031D490
    .word 0x00139510
    .word 0x00156E48
    .word 0x00157688
    .word 0x001576A0
    .word 0x001576B8
    .word 0x001576D0
    .word 0

tg2_update:                       # a0 = gauge
    addiu sp,sp,-16
    sd s0,0(sp)
    sd ra,8(sp)
    move s0,a0
    lui t7,%hi(PARTY)
    lw t6,%lo(PARTY)(t7)          # player 1's hero
    lw t5,0x34(s0)
    beq t6,t5,tg2_go
    nop
    jal GAUGE_F_REFRESH           # character = party slot 4 = player 1's hero (pv_party)
    move a0,s0
    jal GAUGE_SHOWHIDE
    move a0,s0
tg2_go:
    j tg_same                     # the rest as for the twin's small gauge (same stack frame)
    nop

pg_update:                        # a0 = gauge
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    move s0,a0
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    beq t6,zero,pg_u_out          # no twin: nothing to show
    lui t4,0x000F
    li t5,1
    sw t5,{O_PGT}(t4)             # party slot 0 = the twin while this gauge works
    lw t5,0x34(s0)
    beq t5,t6,pg_u_same
    nop
    jal GAUGE_P_REFRESH           # the game's refresh: character (now the twin), face, cached values
    move a0,s0
pg_u_same:
    jal pg_inner
    move a0,s0
    lui t4,0x000F
    sw zero,{O_PGT}(t4)
pg_u_out:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
pg_inner:                         # the game's player gauge update (0x00157F08) without its "party changed" check
    addiu sp,sp,-16
    sd s0,0(sp)
    sd ra,8(sp)
    j 0x00157F1C
    move s0,a0

pg_setup:                         # the game's player gauge set-up (0x001569D8) with our own group (0x32) instead of 3
    addiu sp,sp,-80
    move a2,zero
    sd s2,16(sp)
    j 0x001569E8
    li a3,{PG_BASE}

pv_create:                        # hook 0x0013D9D8 (end of the HUD's gauge creation), before tg_create
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui t7,%hi(MGR_CUR)
    lw t7,%lo(MGR_CUR)(t7)
    lw a0,0x14(t7)                # the layer's owner: its allocator
    lw t6,0(a0)
    lw v0,0(t6)
    li a1,0x15B0                  # size of a friend gauge
    jalr v0
    move a2,zero
    move s0,v0
    jal GAUGE_F_CTOR
    move a0,v0
    lui t6,%hi(tg2_class)
    addiu t6,t6,%lo(tg2_class)
    sw t6,0(s0)
    lui t7,0x000F
    sw s0,{O_TG2}(t7)
    move a0,s0
    move a1,zero
    jal tg_f30
    li a2,3                       # index 3: party slot 4 = player 1's hero; group 0x31
    sw zero,0x380(s0)             # face picture slot 0 (the hero's own)
    lui t7,%hi(MGR_CUR)
    lw t7,%lo(MGR_CUR)(t7)
    lw a0,0x14(t7)
    lw t6,0(a0)
    lw v0,0(t6)
    li a1,0x3D00                  # size of the player gauge
    jalr v0
    move a2,zero
    move s0,v0
    jal GAUGE_P_CTOR
    move a0,v0
    lui t6,%hi(pg_class)
    addiu t6,t6,%lo(pg_class)
    sw t6,0(s0)
    lui t7,0x000F
    sw s0,{O_PG}(t7)
    lui t7,%hi(PARTY)
    lw a1,%lo(PARTY)(t7)          # set up with player 1's hero (always there); the first update takes the twin
    jal pg_setup
    move a0,s0
    ld ra,0(sp)
    ld s0,8(sp)
    j {CHAIN_CREATE}
    addiu sp,sp,32

pv_destroy:                       # hook 0x0013D9E0 (HUD gauges destroyed), before tg_destroy
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000F
    lw a0,{O_TG2}(t7)
    beq a0,zero,pv_d_2
    sw zero,{O_TG2}(t7)
    lw t6,0(a0)
    lw t7,0x10(t6)                # class method 4: destroy and free
    jalr t7
    nop
pv_d_2:
    lui t7,0x000F
    lw a0,{O_PG}(t7)
    beq a0,zero,pv_d_3
    sw zero,{O_PG}(t7)
    lw t6,0(a0)
    lw t7,0x10(t6)
    jalr t7
    nop
pv_d_3:
    ld ra,0(sp)
    j {CHAIN_DESTROY}
    addiu sp,sp,16

pv_pause:                         # hook 0x0013DBA8 (tail of "gauges off"), before tg_pause. a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    jal GRP_NODRAW
    li a0,0x31
    jal GRP_NOUPD
    li a0,0x31
    jal GRP_NODRAW
    li a0,0x32
    jal GRP_NOUPD
    li a0,0x32
    ld ra,0(sp)
    li a0,6
    j {CHAIN_PAUSE}
    addiu sp,sp,16

pv_resume:                        # hook 0x0013DB50 (tail of "gauges on"), before tg_resume. a0 = 6
    addiu sp,sp,-16
    sd ra,0(sp)
    jal GRP_DRAW
    li a0,0x31
    jal GRP_UPD
    li a0,0x31
    jal GRP_DRAW
    li a0,0x32
    jal GRP_UPD
    li a0,0x32
    ld ra,0(sp)
    li a0,6
    j {CHAIN_RESUME}
    addiu sp,sp,16

pv_party:                         # hook 0x0013DDA0 (HUD party getter), before tg_party
    li t6,4
    beq a0,t6,pv_pa_hero          # slot 4 = player 1's hero (for his small gauge)
    lui t7,0x000F
    bne a0,zero,pv_pa_norm
    lw t6,{O_PGT}(t7)
    beq t6,zero,pv_pa_norm
    nop
    lui t6,%hi(V_TWIN)            # slot 0 while player 2's own gauge works = the twin
    jr ra
    lw v0,%lo(V_TWIN)(t6)
pv_pa_hero:
    lui t7,%hi(PARTY)
    jr ra
    lw v0,%lo(PARTY)(t7)
pv_pa_norm:
    j tg_party
    nop
"""


def retarget(hooks, addr, word, section, meaning):
    """Replace the hook at addr (same original word) by a new one."""
    for i, h in enumerate(hooks):
        if h[0] == addr:
            hooks[i] = (addr, word, h[2], section, meaning)
            return
    raise SystemExit("retarget: no hook at %08X" % addr)


def build(names):
    if "views" in names:          # base = merged-v2 + lane V1's two views (snapshot copy of tools/lane-v1/make_v1.py)
        sys.path.append(str(HERE))
        import v1_views
        sections, hooks, _ = v1_views.build(set())
    else:
        sections, hooks = M.build(without={"base"}, v2=True)
    sym = dict(SYM)
    sym["TG_GROUP"] = TG_GROUP
    sym["TG_A3"] = TG_A3
    sym["FACE_SCALE_HI"] = FACE_SCALE >> 16
    j = M.jmp
    if "p2gauge" in names:
        rows, s = M.asm_lines(P2GAUGE_AT, P2GAUGE_SRC, sym)
        sections.append(("p2gauge", "lane V2: interim gauge for player 2 on the one-view HUD (third friend-style gauge bound to the twin)", rows))
        sym.update(s)
        hooks += [
            (0x0013D9D8, j(s["tg_create"]), j(0x0013DB60), "p2gauge", "end of the HUD's gauge creation: also create the twin gauge"),
            (0x0013DBA8, j(s["tg_pause"]), j(0x00139B28), "p2gauge", "tail of 'gauges off' (groups 3-6): also our group"),
            (0x0013DB50, j(s["tg_resume"]), j(0x00139BA0), "p2gauge", "tail of 'gauges on' (groups 3-6): also our group"),
            (0x0013DDA0, j(s["tg_party"]), 0x27BDFFF0, "p2gauge", "HUD party getter: slot 3 = the twin"),
            (0x0013DDA4, 0, 0x0080282D, "p2gauge", "delay slot of the jump above"),
            (0x0013D9E0, j(s["tg_destroy"]), 0x27BDFFF0, "p2gauge", "HUD gauges destroyed: destroy the twin gauge first"),
            (0x0013D9E4, 0, 0xFFB00000, "p2gauge", "delay slot (the two instructions are replayed in tg_destroy)"),
        ]
    chain = {"CHAIN_CREATE": "tg_create", "CHAIN_DESTROY": "tg_destroy", "CHAIN_PAUSE": "tg_pause", "CHAIN_RESUME": "tg_resume"}
    if "marker" in names:
        assert "p2gauge" in names, "marker needs 'p2gauge' too"
        src = MARKER_SRC.format(O_MK1=O_MK1, O_MK2=O_MK2, O_MKK=O_MKK, MK_GROUP=MK_GROUP, MK_DY=MK_DY, MK_STEPS=MK_STEPS)
        rows, s = M.asm_lines(MARKER_AT, src, sym)
        assert rows[-1][0] + 4 <= PERVIEW_AT, "marker section too long"
        sections.append(("marker", "lane V2: '1P' / '2P' markers over the two heroes (the game's own number mark, kept in place)", rows))
        sym.update(s)
        retarget(hooks, 0x0013D9E0, j(s["mk_destroy"]), "marker", "HUD gauges destroyed: the markers, then tg_destroy")
        retarget(hooks, 0x0013DBA8, j(s["mk_pause"]), "marker", "tail of 'gauges off': the markers, then tg_pause")
        retarget(hooks, 0x0013DB50, j(s["mk_resume"]), "marker", "tail of 'gauges on': the markers, then tg_resume")
        chain = {"CHAIN_CREATE": "tg_create", "CHAIN_DESTROY": "mk_destroy", "CHAIN_PAUSE": "mk_pause", "CHAIN_RESUME": "mk_resume"}
    if "perview" in names:
        assert "views" in names and "p2gauge" in names, "perview needs 'views' and 'p2gauge' too"
        src = PERVIEW_SRC.format(O_VON=O_VON, O_LIVE=O_LIVE, O_DREW=O_DREW, O_PMODE=O_PMODE, O_NTH=O_NTH,
                                 O_TG2=O_TG2, O_PG=O_PG, O_PGT=O_PGT, PG_BASE=PG_GROUP - 3, MK_GROUP=MK_GROUP, **chain)
        rows, s = M.asm_lines(PERVIEW_AT, src, sym)
        assert rows[-1][0] + 4 <= 0x000F7F00, "perview section too long"
        sections.append(("perview", "lane V2: each player's own field HUD is drawn into that player's view picture (two-view mode)", rows))
        hooks += [
            (0x00161A40, j(s["pv_first"]), 0x27BDFFF0, "perview", "two-view task 90000: draw player 1's HUD (it lands in player 1's view picture)"),
            (0x00161A44, 0, 0xFFBF0000, "perview", "delay slot (the task's body was only a jump to 0x0014E0D8)"),
            (0x00161C70, j(s["pv_second"]), 0x27BDFFF0, "perview", "two-view task 90130, before the two pictures are put on screen: draw player 2's HUD (it lands in player 2's view picture)"),
            (0x00161C74, 0, 0xFFBF0000, "perview", "delay slot (the two instructions are replayed in pv_second)"),
            (0x00139390, j(s["pv_mgr"]), 0x27BDFFF0, "perview", "HUD manager task (priority 100000): skip when the HUD went into the view pictures"),
            (0x00139394, 0, 0x3C0F0034, "perview", "delay slot (replayed in pv_mgr)"),
            (0x001393D8, j(s["pv_end"]), j(0x00139DC0), "perview", "field HUD task removed: forget the HUD"),
            (0x0013921C, M.jal(s["pv_ufilter"]), 0x8E0F000C, "perview", "HUD object's task: which objects are updated in this run"),
            (0x00139220, 0, 0x31EF0020, "perview", "delay slot (the flag test moved into pv_ufilter)"),
            (0x0013935C, M.jal(s["pv_filter"]), 0x8C8F000C, "perview", "HUD draw-all: which objects are drawn into this picture"),
            (0x00139360, 0x0220282D, 0x31EE0040, "perview", "delay slot: a1 = manager (the flag tests moved into pv_filter)"),
        ]
        retarget(hooks, 0x0013D9D8, j(s["pv_create"]), "perview", "end of the HUD's gauge creation: player 2's gauges, then tg_create")
        retarget(hooks, 0x0013D9E0, j(s["pv_destroy"]), "perview", "HUD gauges destroyed: player 2's gauges, then tg_destroy")
        retarget(hooks, 0x0013DBA8, j(s["pv_pause"]), "perview", "tail of 'gauges off': groups 0x31, 0x32, then tg_pause")
        retarget(hooks, 0x0013DB50, j(s["pv_resume"]), "perview", "tail of 'gauges on': groups 0x31, 0x32, then tg_resume")
        retarget(hooks, 0x0013DDA0, j(s["pv_party"]), "perview", "HUD party getter: slot 4 = hero, slot 0 = twin for player 2's gauge, then tg_party")
    return sections, hooks


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    out = pathlib.Path(args[0])
    names = set(args[1:])
    sections, hooks = build(names)
    word = M.load_elf_words()
    code, hook_words, problems = {}, {}, []
    for name, _, rows in sections:
        for addr, w, _, _, _ in rows:
            if addr in code:
                sys.exit("CLASH: code address %08X used by two sections" % addr)
            code[addr] = w
    for addr, w, orig, name, _ in hooks:
        if addr in hook_words or addr in code:
            sys.exit("CLASH: hook address %08X used twice" % addr)
        hook_words[addr] = w
        have = word(addr)
        if have is None:
            problems.append("hook %08X is outside the program file" % addr)
        elif orig is not None and have != orig:
            problems.append("hook %08X: program has %08X, expected %08X" % (addr, have, orig))
    for a in code:
        if word(a) is not None:
            problems.append("code address %08X is inside the program file" % a)
    if problems:
        sys.exit("PROBLEMS:\n  " + "\n  ".join(problems))
    out.mkdir(parents=True, exist_ok=True)
    mine = sorted(n for n in names)
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project: merged build v2 + lane V2 sections [%s] (tools/lane-v2/make_v2.py)." % ", ".join(mine),
             "comment=Every PC in an online game must have this same file (it changes game code)."]
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hook_words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hook_words[a]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    lst = ["Lane V2 patch for CRC F266B00B = merged-v2 + [%s]. Every word the patch file writes, with its meaning." % ", ".join(mine), ""]
    for name, title, rows in sections:
        lst.append("=" * 100)
        lst.append("SECTION %s: %s" % (name, title))
        lst.append("  cave 0x%08X-0x%08X (%d words)" % (rows[0][0], rows[-1][0] + 3, len(rows)))
        for addr, w, labels, src, comment in rows:
            for lab, lc in labels:
                lst.append("%s:%s" % (lab, ("    # " + lc) if lc else ""))
            lst.append("  %08X  %08X  %-34s%s" % (addr, w, mips.dis(w, addr), ("# " + comment) if comment else ""))
        lst.append("")
    lst.append("=" * 100)
    lst.append("HOOKS (words changed inside the game program)")
    for addr, w, orig, name, meaning in sorted(hooks):
        have = word(addr)
        lst.append("  %08X  %08X  %-26s was %08X %-28s [%s] %s" % (addr, w, mips.dis(w, addr), have, mips.dis(have, addr), name, meaning))
    lst.append("")
    lst.append("LANE V2 VARIABLES (not written by the patch file; they rely on that memory being zero at boot)")
    for k in ("V_TG", "V_TGH"):
        lst.append("  %08X  %s" % (SYM[k], k))
    for off, k in ((O_LIVE, "V_LIVE   field HUD manager whose scene task ran in the last step (0 = none)"),
                   (O_DREW, "V_DREW   manager already updated and drawn into the view pictures in this step"),
                   (O_PMODE, "V_PMODE  picture being drawn: 0 = one view, 1 = player 1's, 2 = player 2's"),
                   (O_NTH, "V_NTH    number of HUD runs done in this step"),
                   (O_TG2, "V_TG2    small gauge of player 1's hero (drawn in player 2's picture)"),
                   (O_PG, "V_PG     player 2's own big gauge"),
                   (O_PGT, "V_PGT    1 while player 2's own gauge works (HUD party slot 0 = the twin)"),
                   (O_MK1, "V_MK1    marker over player 1's hero"),
                   (O_MK2, "V_MK2    marker over the twin"),
                   (O_MKK, "V_MKK    test knob: animation steps for new markers (0 = the built-in number)")):
        lst.append("  %08X  %s" % (0x000F0000 + off, k))
    (out / "listing.txt").write_text("\n".join(lst) + "\n")
    n_mine = sum(len(r) for n, _, r in sections if n in ("p2gauge", "perview", "marker"))
    print("%d code words (%d of this lane), %d hook words -> %s" % (len(code), n_mine, len(hook_words), out / "SLPM-66675_F266B00B.pnach"))


if __name__ == "__main__":
    main()
