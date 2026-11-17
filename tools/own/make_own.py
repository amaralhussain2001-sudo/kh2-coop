"""OWN SCREENS: join lane V1 (two full-size views), lane V2 (a HUD per player) and the current merged build.

  python -I tools/own/make_own.py [outDir] [--base merged-v6] [--no-perview] [--plain] [--vopt=OPTION ...] [--cannon1view] [--cannon2view]

  default    tools/own/views.py in its KEEP mode (see tools/own/fork_views.py): lane V1's delivered arrangement plus
             two markers; the own-view emulator (build view12 or later) keeps a sharp copy of player 1's picture and
             puts it over the one the game reloads at the PS2's own resolution.
  --plain    lane V1's own generator, no markers (player 1's 3D picture has native sharpness on any emulator).
  --vopt=    experiments: options handed to tools/own/views.py (park, late, ...).

Result = the merged build (--base, default patches/merged-v6) + lane V1's sections "views" and "views-data"
(built by tools/own/views.py = lane V1's current generator + the park change; layout 2 = two full pictures)
+ lane V2's sections "p2gauge" and "perview" (tools/lane-v2/make_v2.py; no 1P/2P markers: user decision)
+ the ring rule of merged build 5 for the second small gauge (player 1's hero in player 2's picture).

How it is put together, word by word:
  1. OWN  = lane V2's generator output for {views, p2gauge, perview}, with lane V1's current generator in place of
            lane V2's old snapshot (v1_views.py). This is "merged-v2 + V1 + V2".
  2. A    = patches/lane-v2-p2gauge ("merged-v2 + p2gauge"), the form of lane V2 that is inside the merged build.
  3. D    = what the merged build adds to, changes in or removes from A (lanes R, H, N, B75, the glue routines).
  4. Checks: OWN agrees with A on every word of A except the five hook words lane V2's per-view section re-aims
            on purpose; no address of D is one that OWN added or re-aimed. Then RESULT = OWN with D applied.
Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v6-own.
"""
import hashlib
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})")
REAIMED = {0x0013D9D8, 0x0013D9E0, 0x0013DBA8, 0x0013DB50, 0x0013DDA0}   # lane V2 per-view: pv_* in front of tg_*
RINGS2_AT = 0x000F34D0            # after the ring routine of merged build 5 (0x000F3440-0x000F34CB)
RINGS_COMMON = 0x000F3454         # merged build 5's ring routine, just after its call of the gauge's own update


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_patch(folder):
    order, words = [], {}
    for raw in (ROOT / "patches" / folder / NAME).read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        assert m.group(1) == "1" and m.group(3).lower() == "word", raw
        a = int(m.group(2), 16)
        assert a not in words, "address twice in %s: %08X" % (folder, a)
        order.append(a)
        words[a] = int(m.group(4), 16)
    return order, words


def load_listing(folder):
    origin = {}
    p = ROOT / "patches" / folder / "listing.txt"
    for raw in p.read_text(encoding="utf-8").splitlines():
        parts = raw.split(None, 2)
        if len(parts) == 3 and re.fullmatch(r"[0-9A-Fa-f]{8}", parts[0]) and re.fullmatch(r"[0-9A-Fa-f]{8}", parts[1]):
            origin[int(parts[0], 16)] = parts[2]
    return origin


ROWS_AT = 0x000F4000              # routines of step 7 (0x000F4000-0x000F4FFF was lane S1's range; never used)
ROWS_END = 0x000F4400
O_CSD, O_CSW = 0x4400, 0x4404     # variables (offsets from 0x000F0000; they rely on zero memory at boot)
O_SH = 0x4410                     # player 2's copy of display+0x18..+0x103 (0xEC bytes) while it is not swapped in
O_POOL2, O_EFF2, O_OBJ2 = 0x4500, 0x4504, 0x4508   # player 2's set of the display's pools (see own_pools)
ROWS_DATA_END = 0x000F450C
ROWS_SRC = """
own_hud:                          # in place of lane V2's pv_hud (both calls). a0 = 0 player 1, 1 player 2
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s2,a0
    lui s1,0x000F
    lui t7,%hi(CMD_DISPLAY)
    lw s0,%lo(CMD_DISPLAY)(t7)    # the command menu display
    beq s0,zero,oh_plain
    nop
    lw t6,{O_LIVE}(s1)
    beq t6,zero,oh_plain          # no field HUD in this scene: pv_hud does nothing
    ori t4,s1,0x1000              # S2 = player 2's control object (lane G)
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1260              # a built control object starts with this class table
    beq t3,t2,oh_s2
    nop
    jal own_killrows              # player 2 has no control object now: his rows end
    nop
    b oh_plain
    sw zero,{O_CSD}(s1)
oh_s2:
    lw t5,{O_CSD}(s1)
    beq t5,s0,oh_have
    nop
    jal {FRESH}                 # first run with this display: player 2's state starts empty
    nop
    sw s0,{O_CSD}(s1)
oh_have:
    bne s2,zero,oh_p2
    nop
    lbu t6,0xFE(s0)               # player 1's run: "the Reaction Command changed" (set by either control object
    lbu t5,{SH_FE}(s1)            # through the one display pointer) is for both players' menus
    or t5,t5,t6
    sb t5,{SH_FE}(s1)
oh_plain:
    jal PV_HUD
    move a0,s2
    b oh_out
    nop
oh_p2:
    jal {SWAP}                  # player 2's rows and list state go into the display
    move a0,s0
    lbu t6,{SH_FD}(s1)            # "the menu is revealed" (display+0xFD; the game hides and shows the whole row
    sb t6,0xFD(s0)                # group by it, 0x0013D3F8): one state for both players, here player 1's
    li t6,1
    sw t6,{O_CSW}(s1)
    jal PV_HUD
    li a0,1
    addiu t6,s0,0x18              # every row the display holds now is player 2's: mark it
    addiu t5,s0,0xA8
    lui t3,0x4000
oh_m:
    lw t4,0(t6)
    beq t4,zero,oh_mn
    nop
    lw t2,12(t4)
    or t2,t2,t3
    sw t2,12(t4)
oh_mn:
    addiu t6,t6,4
    bne t6,t5,oh_m
    nop
    lbu t6,0xFD(s0)               # revealed in player 2's run (his button, his Reaction Command): for both
    sb t6,{SH_FD}(s1)
    jal {SWAP}                  # player 1's rows and list state come back
    move a0,s0
    sw zero,{O_CSW}(s1)
oh_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,32

own_swap:                         # exchange display+0x18..+0x103 with player 2's copy. a0 = display. t2-t7
    lui t7,0x000F
    addiu t6,t7,{O_SH}
    addiu t5,a0,0x18
    addiu t4,a0,0x104
os_l:
    lw t3,0(t5)
    lw t2,0(t6)
    sw t2,0(t5)
    sw t3,0(t6)
    addiu t5,t5,4
    bne t5,t4,os_l
    addiu t6,t6,4
    jr ra
    nop

own_fresh:                        # player 2's copy = the state of a display that shows nothing (as the game's
    lui t7,0x000F                 # constructor 0x0013B088 and reset 0x0013B128 leave it). t4-t7
    addiu t6,t7,{O_SH}
    addiu t5,t6,0xB4              # +0x18..+0xCB: 36 rows, 36 row bytes
of_z:
    sw zero,0(t6)
    addiu t6,t6,4
    bne t6,t5,of_z
    nop
    li t4,-1
    addiu t5,t6,0x24              # +0xCC..+0xEF: 4 + 4 level words and the menu id = -1
of_m:
    sw t4,0(t6)
    addiu t6,t6,4
    bne t6,t5,of_m
    nop
    sw zero,0(t6)                 # +0xF0
    sw t4,4(t6)                   # +0xF4
    sw t4,8(t6)                   # +0xF8
    sw zero,12(t6)                # +0xFC..+0xFF
    jr ra
    sw zero,16(t6)                # +0x100

own_killrows:                     # player 2's rows end: each one gets "dead" (the manager's sweep gives it back
    lui t7,0x000F                 # to the pool), his copy starts empty. Keeps a0. t3-t7
    lw t6,{O_CSD}(t7)
    beq t6,zero,ok_out            # he has no state
    lw t5,{O_CSW}(t7)
    bne t5,zero,ok_out            # (never: his state is inside the display right now)
    addiu t6,t7,{O_SH}
    addiu t5,t6,0x90
ok_l:
    lw t4,0(t6)
    beq t4,zero,ok_n
    nop
    lw t3,12(t4)
    ori t3,t3,1
    sw t3,12(t4)
ok_n:
    addiu t6,t6,4
    bne t6,t5,ok_l
    nop
    j own_fresh
    nop
ok_out:
    jr ra
    nop

own_forget:                       # hook 0x0013B128: the display forgets its rows (HUD start, reset). a0 = display
    addiu sp,sp,-16
    sd ra,0(sp)
    jal own_killrows
    nop
    lui t7,0x000F
    sw zero,{O_CSD}(t7)
    ld ra,0(sp)
    addiu sp,sp,16
    addiu t7,zero,-1              # the instruction that sat at 0x0013B128
    j 0x0013B130
    daddu t3,zero,zero            # (0x0013B12C again: our routines used t3)

own_d4c8:                         # hook 0x0013D4C8: the display removes all its rows (the menu changes its look)
    addiu sp,sp,-16               # the instruction that sat there
    sd ra,8(sp)
    jal own_killrows
    nop
    ld ra,8(sp)
    j 0x0013D4D0
    lui t7,0x45                   # (0x0013D4CC again: our routines used t7)

own_gone:                         # hook 0x0013B498 (jal): the display object ends (its pool is already freed)
    lui t7,%hi(CMD_DISPLAY)
    sw zero,%lo(CMD_DISPLAY)(t7)  # the instruction that sat there
    lui t7,0x000F
    sw zero,{O_CSD}(t7)
    jr ra
    sw zero,{O_CSW}(t7)

own_pools:                        # hook 0x0013B394 (jal 0x0013AD20): a new display gets its pools (36 rows, ...).
    addiu sp,sp,-16               # One root menu takes 9 rows, a list up to 9 more per level: two players' lists
    sd ra,0(sp)                   # together can want more than 36. So the game's routine runs twice, and the
    jal 0x0013AD20                # first set is player 2's.
    nop
    lui t7,0x0035
    lui t6,0x000F
    lw t5,-32680(t7)              # 0x00348058: the pool of rows
    sw t5,{O_POOL2}(t6)
    lw t5,-32684(t7)              # 0x00348054: the pool of flash effects (not used by player 2; freed with the rest)
    sw t5,{O_EFF2}(t6)
    lw t5,-32688(t7)              # 0x00348050: the layout holder
    sw t5,{O_OBJ2}(t6)
    ld ra,0(sp)
    j 0x0013AD20                  # the game's own set (the three pointers are written again)
    addiu sp,sp,16

own_unpools:                      # hook 0x0013B474 (jal 0x0013AED8): the display's pools are freed
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x0013AED8                # the game's set; the three pointers are zero afterwards
    nop
    lui t6,0x000F
    lw t5,{O_POOL2}(t6)
    beq t5,zero,oup_done
    lui t7,0x0035
    sw t5,-32680(t7)
    lw t5,{O_EFF2}(t6)
    sw t5,-32684(t7)
    lw t5,{O_OBJ2}(t6)
    sw t5,-32688(t7)
    sw zero,{O_POOL2}(t6)
    sw zero,{O_EFF2}(t6)
    jal 0x0013AED8                # player 2's set, by the same routine
    sw zero,{O_OBJ2}(t6)
oup_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

own_alloc:                        # hook 0x0013ACC0: a new row is taken. t7 = 0x00350000. Out: s0 = the pool
    lw s0,-32680(t7)              # the instruction that sat there: the game's pool
    lui t6,0x000F
    lw t7,{O_CSW}(t6)
    beq t7,zero,oal_done          # not player 2's run
    lw t7,{O_POOL2}(t6)
    beq t7,zero,oal_done
    nop
    move s0,t7                    # player 2's display takes its rows from player 2's pool
oal_done:
    j 0x0013ACC8
    nop

own_rel:                          # hook 0x0013AB28: a row goes back to its pool. a0 = row, t7 = 0x00350000.
    lw t4,-32680(t7)              # Out: t4 = the pool it came from (the instruction that sat there: the game's)
    lui t6,0x000F
    lw t6,{O_POOL2}(t6)
    beq t6,zero,orl_done
    sltu t3,a0,t6
    bne t3,zero,orl_done          # below player 2's pool
    addiu t3,t6,0x6E40
    sltu t3,a0,t3
    movn t4,t6,t3                 # inside player 2's pool
orl_done:
    j 0x0013AB30
    nop

own_filter:                       # hook 0x0013935C (jal), in front of lane V2's pv_filter. a0 = object, a1 = manager
    lw t5,0(a0)
    lui t2,0x0035
    addiu t2,t2,-31312            # 0x003485B0: a row of the command menu
    bne t5,t2,ofi_go
    lui t4,0x000F
    lw t7,12(a0)
    lw t3,{O_PMODE}(t4)           # 0 = one view, 1 = player 1's picture, 2 = player 2's picture
    srl t5,t7,30
    andi t5,t5,1                  # 1 = player 2's row
    addiu t3,t3,-2
    sltiu t3,t3,1                 # 1 = player 2's picture
    bne t5,zero,ofi_p2
    lw t2,{O_CSW}(t4)
    and t3,t3,t2                  # player 1's row: not in player 2's picture while he has rows of his own
    bne t3,zero,ofi_hide
    nop
ofi_go:
    j {FGO}
    nop
ofi_p2:
    bne t3,zero,ofi_go            # player 2's row: in player 2's picture only
    nop
ofi_hide:
    ori t7,t7,2
    jr ra
    andi t6,t7,0x40

own_ufilter:                      # hook 0x0013921C (jal), in front of lane V2's pv_ufilter. s0 = object.
    lw t5,0(s0)                   # Out: t7 != 0 = no update now
    lui t2,0x0035
    addiu t2,t2,-31312
    bne t5,t2,ouf_go
    lui t4,0x000F
    lw t7,12(s0)
    lw t3,{O_PMODE}(t4)
    srl t5,t7,30
    andi t5,t5,1
    addiu t3,t3,-2
    sltiu t3,t3,1
    bne t5,zero,ouf_p2
    lw t2,{O_CSW}(t4)
    and t3,t3,t2
    bne t3,zero,ouf_skip
    nop
ouf_go:
    j PV_UFILTER
    nop
ouf_p2:
    bne t3,zero,ouf_go
    nop
ouf_skip:
    jr ra
    ori t7,zero,0x20
"""


BOSSV_AT = 0x000F5C00             # step 8: boss moves keep two views (0x000F5C00-0x000F5E7F; variable 0x000F5E80)
BOSSV_END = 0x000F5E80
CN_AT = 0x000F7400                # (--cannon2view) the toy cannon's view for each player: 0x000F7400-0x000F74FF
CN_END = 0x000F7500
CN_SRC = """
cn_view:                          # from bm_cam2 while the twin is a toy cannon. a0 = the camera (player 2's camera is in the game's camera memory)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    lui t7,0x000F
    addiu t0,t7,0x6E00            # camera 1, as the game left it (it sits in player 2's store while camera 2 is in)
    move t1,a0
    addiu t2,zero,60              # 0xF0 bytes
cv_cp:
    lw t3,0(t0)
    addiu t0,t0,4
    sw t3,0(t1)
    addiu t2,t2,-1
    bne t2,zero,cv_cp
    addiu t1,t1,4
    lw t9,0x05CC(t7)              # the twin
    sw t9,0x44(a0)                # camera 2's target
    lui t5,0x0035
    lw t8,-5816(t5)               # the engine's player (player 1's cannon)
    beq t8,zero,cv_view
    nop
    lwc1 f0,0x70(t9)              # the way from player 1's cannon to the twin's
    lwc1 f1,0x70(t8)
    lwc1 f2,0x74(t9)
    lwc1 f3,0x74(t8)
    lwc1 f4,0x78(t9)
    lwc1 f5,0x78(t8)
    sub.s f0,f0,f1
    sub.s f2,f2,f3
    sub.s f4,f4,f5
    jal cv_add
    move t3,a0                    # + 0x00: the aim point
    jal cv_add
    addiu t3,a0,0x10              # + 0x10: the eye
    jal cv_add
    addiu t3,a0,0x60              # + 0x60, + 0x70: the wished eye
    jal cv_add
    addiu t3,a0,0x70
    jal cv_add
    addiu t3,a0,0x80              # + 0x80, + 0x90: the wished aim point
    jal cv_add
    addiu t3,a0,0x90
cv_view:
    ld a0,8(sp)
    jal 0x001408A0                # the game writes the view from this camera (the caller chose view 1)
    move a1,zero
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
cv_add:                           # t3 = a place (x, y, z)
    lwc1 f6,0(t3)
    lwc1 f7,4(t3)
    lwc1 f8,8(t3)
    add.s f6,f6,f0
    add.s f7,f7,f2
    add.s f8,f8,f4
    swc1 f6,0(t3)
    swc1 f7,4(t3)
    jr ra
    swc1 f8,8(t3)
"""
BOSSV_SRC = """
    j bm_hold                     # 0x000F5C00
    nop
    j bm_cam1                     # 0x000F5C08
    nop
    j bm_cam2                     # 0x000F5C10
    nop
bm_who:                           # v0 = 0 no hold, 1 one view wanted, 2 player 1's hero is in a scripted move, 3 the twin is
    lui t7,0x000F
    lw t8,0x05CC(t7)              # the twin
    beq t8,zero,bw_one            # no twin in this room
    lui t2,0x0034
    lw t3,-13256(t2)              # 0x0033CC38: an event holds the camera
    beq t3,zero,bw_none
    lui t4,0x0035
    lw t5,0x037C(t4)              # 0x0035037C: the event object
    beq t5,zero,bw_one
    lw t9,-5816(t4)               # player 1's hero
    beq t9,zero,bw_one
    nop
    lw t6,8(t5)                   # who started the event: an object (0x0180xxxx-0x01BFxxxx) = a scripted move;
    srl t6,t6,22                  # the mission / the room / nobody = a story scene
    li t0,6
    bne t6,t0,bw_one
    nop
    lw t0,0x160(t9)               # bit 0x4000: this hero is in a scripted move
    lw t1,0x160(t8)
    srl t0,t0,14
    srl t1,t1,14
    andi t0,t0,1
    andi t1,t1,1
    beq t0,t1,bw_one              # both or neither: one view, as before
    nop
    bne t1,zero,bw_twin
    nop
    jr ra
    li v0,2
bw_twin:
    jr ra
    li v0,3
bw_one:
    jr ra
    li v0,1
bw_none:
    jr ra
    move v0,zero
bm_hold:                          # v0 = 1 when one view is wanted
    addiu sp,sp,-16
    sd ra,0(sp)
    jal bm_who
    nop
    li t0,1
    beq v0,t0,bh_end
    ld ra,0(sp)
    move v0,zero
bh_end:
    jr ra
    addiu sp,sp,16
bm_copy:                          # t0 = from, t1 = to, t2 = words
    lw t3,0(t0)
    addiu t2,t2,-1
    sw t3,0(t1)
    addiu t0,t0,4
    bne t2,zero,bm_copy
    addiu t1,t1,4
    jr ra
    nop
bm_cam1:                          # camera 1's update (a0 = the camera, a1 = 0)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    move s0,a0
    lui t7,0x000F
    lw t0,0x6F04(t7)              # are two views on?
    beq t0,zero,b1_plain
    nop
    jal bm_who
    nop
    li t0,3
    bne v0,t0,b1_plain            # the twin is not the hero of a scripted move: camera 1 as the game does it
    nop
    lui t0,0x003A                 # the move's picture (view 0's data) -> view 1's data: player 2 sees his hero's move
    ori t0,t0,0x7B70
    addiu t1,t0,0x100
    jal bm_copy
    li t2,64
    lui t0,0x003A
    ori t0,t0,0x7D70
    addiu t1,t0,0x100
    jal bm_copy
    li t2,64
    lui t0,0x003A
    ori t0,t0,0x7F70
    addiu t1,t0,0x90
    jal bm_copy
    li t2,36
    lui t0,0x003A
    ori t0,t0,0x8090
    addiu t1,t0,0x90
    jal bm_copy
    li t2,36
    lui t7,0x000F
    li t0,1
    sw t0,0x5E80(t7)              # camera 2 leaves view 1 alone in this step
    lui t2,0x0034
    lw t3,-13256(t2)
    sd t3,16(sp)
    sw zero,-13256(t2)            # camera 1 goes on for player 1's hero although the move holds the camera
    move a0,s0
    jal 0x00140B68
    move a1,zero
    ld t3,16(sp)
    lui t2,0x0034
    b b1_end
    sw t3,-13256(t2)
b1_plain:
    move a0,s0
    jal 0x00140B68
    move a1,zero
b1_end:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
bm_cam2:                          # camera 2's update (a0 = the camera, a1 = 0; player 2's camera is swapped in)
    lui t7,0x000F
    lw t0,0x5E80(t7)
    beq t0,zero,b2_go
    lui t2,0x0034
    jr ra                         # the move's picture is in view 1 already
    sw zero,0x5E80(t7)
b2_go:
    lw t3,-13256(t2)
    bne t3,zero,b2_hold
    nop
    j 0x00140B68
    nop
b2_hold:                          # a scripted move holds the camera: camera 2 goes on for the twin
    addiu sp,sp,-16
    sd ra,0(sp)
    sd t3,8(sp)
    jal 0x00140B68
    sw zero,-13256(t2)
    ld t3,8(sp)
    lui t2,0x0034
    sw t3,-13256(t2)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""


LOOK_AT = 0x000F3B00              # step 9: the command menu's frame and picture sheet per player. Routines
LOOK_END = 0x000F3FF0             # 0x000F3B00-0x000F3FEF, data 0x000F3900-0x000F3A9F (all zero in a run: probe e2-sheet)
O_LK2, O_TX2, O_WTX, O_BIN, O_H1 = 0x3900, 0x3904, 0x3908, 0x390C, 0x3910
O_B = 0x3914                      # player 2's copy: +0 frame flags, +4 board look, +8 the frame's content (0x180 bytes)
LOOK_DATA_END = 0x000F3AA0
PG_GLINT = """            lw t7,52(s0)              # seventh round, the orange glint beside player 2's gauge: the gauge's glow
            beq t7,zero,pr_glow       # part (+0x52C, sequence 27) belongs on the gauge only while the clock
            nop                       # slot + 448 runs (the game's test 0x001A1DE0; routine 0x00157AE0 hides
            lw t7,1164(t7)            # the part when the clock stops). Player 2's gauge is built before it
            beq t7,zero,pr_glow       # has its hero, and a gauge with no hero shows the part (0x00156540 with
            nop                       # 0x00155EE8 = 21); with no change of state afterwards nothing hid it.
            lwc1 f1,448(t7)           # Here: no clock running = hidden, as player 1's is.
            mtc1 zero,f0              # Option --no-glint leaves it out.
            c.lt.s f0,f1
            bc1t pr_glow
            nop
            lw t6,0x538(s0)
            ori t6,t6,0x40
            sw t6,0x538(s0)
        pr_glow:
"""
PG_GUARD = """            lw t7,52(a0)              # seventh round (found by the mission sweep, EH14_MS103: 5 fault lines in one
            beq t7,zero,pr_go         # frame at the start of the fight): the gauge has its hero, but the hero has
            nop                       # no unit slot in that frame, and the game's gauge update reads the gauge
            lw t7,1164(t7)            # kind (slot + 431) and the clock (slot + 448) through 0. No slot = no
            bne t7,zero,pr_go         # update in this frame. (A gauge without a hero is the game's own case and
            nop                       # goes on as before.) Option --no-pgguard leaves it out.
            jr ra
            nop
        pr_go:
"""
LOOK_PLAIN = """    jr ra
    sw t4,-32688(t5)
"""
LOOK_HIDE = """    sw t4,-32688(t5)
    lw t2,0x110(a0)               # seventh round: his frame is hidden while the game hides player 1's. The
    lw t6,{O_B}(t7)               # HUD's "hide this group" (flag bits 0x22: READY GO of a small game, a scene)
    ori t2,t2,0x22                # reaches only the frame that is in the HUD lists, and that is player 1's;
    xori t2,t2,0x22               # player 2's copy stayed in sight with no sheet behind it: a grey square
    andi t6,t6,0x22               # on his screen for the three seconds of READY GO (tests r11-skate-retry-p2,
    or t2,t2,t6                   # r40-skate-start-fine). Player 1's two bits are copied into his word each
    jr ra                         # time his state goes into the display. Option --no-lookhide leaves it out.
    sw t2,0x110(a0)
"""
LOOK_SRC = """
own_swap2:                        # in place of own_swap in own_hud (both calls). a0 = display. Keeps a0
    addiu sp,sp,-16
    sd ra,0(sp)
    jal OWN_SWAP                  # the rows and the list state
    nop
    ld ra,0(sp)
    addiu sp,sp,16                # (falls into look_swap on purpose)
look_swap:                        # exchange the frame's state with player 2's copy and put the other holder in.
    lui t7,0x000F                 # a0 = display. Keeps a0. t2-t7
    lw t3,0x110(a0)               # the frame object's flag word
    lw t2,{O_B}(t7)
    sw t2,0x110(a0)
    sw t3,{O_B}(t7)
    lw t3,0x2A0(a0)               # the board look while a board menu is open
    lw t2,{O_B4}(t7)
    sw t2,0x2A0(a0)
    sw t3,{O_B4}(t7)
    addiu t6,t7,{O_B8}
    addiu t5,a0,0x11C             # the frame's sequence player and its own words, up to the control object pointer
    addiu t4,a0,0x29C
ls_l:
    lw t3,0(t5)
    lw t2,0(t6)
    sw t2,0(t5)
    sw t3,0(t6)
    addiu t5,t5,4
    bne t5,t4,ls_l
    addiu t6,t6,4
    lw t6,{O_BIN}(t7)
    lui t5,0x0035
    bne t6,zero,ls_back
    lw t3,-32688(t5)              # 0x00348050: the layout holder (it carries the picture sheet)
    lw t4,{O_OBJ2}(t7)            # going in: player 2's holder takes the place of the game's
    sw t3,{O_H1}(t7)
    movz t4,t3,t4                 # (he has none: the game's stays)
    li t6,1
    sw t6,{O_BIN}(t7)
@LOOKHIDE@ls_back:
    lw t3,{O_H1}(t7)              # going out: the game's holder again
    sw zero,{O_BIN}(t7)
    jr ra
    sw t3,-32688(t5)

look_fresh2:                      # in place of own_fresh in own_hud: player 2's state is made anew. s0 = display
    addiu sp,sp,-16
    sd ra,0(sp)
    jal OWN_FRESH
    nop
    jal look_build
    move a0,s0
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

look_build:                       # player 2's frame and sheet from nothing, as the game makes its own (0x0013D208)
    addiu sp,sp,-48               # but without a second entry in the HUD's lists. a0 = display; his state is out
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s0,a0
    jal look_swap                 # his copy in (what it held is not used), his holder in
    lui s1,0x000F
    lw s3,0x29C(s0)
    ori t6,s1,0x1000
    sw t6,0x29C(s0)               # the display reads his control object (S2) while his frame is made
    sw zero,0x110(s0)
    jal 0x00239700                # an empty sequence player
    addiu a0,s0,0x11C
    lui t7,0x0035
    lw a0,-32688(t7)              # his holder
    lw s2,{O_LK2}(s1)
    sw s2,0x2A0(s0)
    beq s2,zero,lb_world
    nop
    b lb_sheet                    # his board menu is open: the board's sheet and look
    lw a1,{O_TX2}(s1)
lb_world:
    lw s2,0x2A4(s0)               # the world's own look (0 = the game's default one)
    beq s2,zero,lb_defsheet
    lw a1,{O_WTX}(s1)             # and the world's own sheet
    bne a1,zero,lb_sheet
    nop
lb_defsheet:
    lui t7,0x0034
    lw a1,32736(t7)               # 0x00347FE0: the default sheet
lb_sheet:
    jal 0x00138698                # the holder's sheet (a0 = holder, a1 = sheet data)
    nop
    bne s2,zero,lb_frame
    nop
    lui t7,0x0034
    lw s2,32740(t7)               # 0x00347FE4: the default look
lb_frame:
    jal 0x00138748                # the frame object's own words
    addiu a0,s0,0x104
    lui t7,0x0035
    lw a2,-32688(t7)
    lw a3,-31368(t7)              # 0x00348578: the frame's first sequence
    addiu a2,a2,32
    move a1,s2
    jal 0x001387F8                # look, sheet, sequence
    addiu a0,s0,0x104
    addiu a0,s0,0x104
    li a1,28
    jal 0x00138C40                # its place on the screen
    li a2,322
    lui t7,0x0035
    lw t7,-31364(t7)              # 0x0034857C: the sequence that follows
    sw t7,0x28C(s0)
    jal 0x0013B2A8                # f0 = the frame's fade value
    move a0,s0
    lui t7,0x0037
    lwc1 f12,-21156(t7)           # 0x0036AD5C
    mov.s f15,f0
    mov.s f13,f12
    mov.s f14,f12
    jal 0x00138D48                # its colour
    addiu a0,s0,0x104
    jal 0x0013D1D0                # hidden while his control object says so
    move a0,s0
    sw s3,0x29C(s0)
    jal look_swap                 # out again
    move a0,s0
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,48

look_hold:                        # in place of the two calls of 0x0013B1D0 (a new display, a HUD restart): the
    addiu sp,sp,-16               # game makes its holder a HUD object with the default sheet; player 2's too
    sd ra,0(sp)
    jal 0x0013B1D0
    nop
    lui t7,0x000F
    lw t6,{O_OBJ2}(t7)
    beq t6,zero,lh_out
    lui t5,0x0035
    lw t4,-32688(t5)
    sd t4,8(sp)
    jal 0x0013B1D0
    sw t6,-32688(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-32688(t5)
lh_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

look_on:                          # in place of the call of 0x0013D550 at 0x001D4840 (a control object opens its
    lui t7,0x000F                 # board menu: the board's sheet and look). a0 = sheet, a1 = look, s1 = the record
    ori t6,t7,0x1000              # inside that control object
    sltu t5,s1,t6
    bne t5,zero,lo_game
    addiu t6,t6,0xB00
    sltu t5,s1,t6
    beq t5,zero,lo_game
    nop
    sw a1,{O_LK2}(t7)             # player 2's control object: remembered for a frame that is made later
    sw a0,{O_TX2}(t7)
    lui t9,0x0013
    j look_p2
    ori t9,t9,0xD550
lo_game:
    j 0x0013D550
    nop

look_off:                         # in place of the call of 0x0013D620 at 0x001D48C8 (the board menu closes: the
    lui t7,0x000F                 # default sheet and look again). s0 = the record inside the control object
    ori t6,t7,0x1000
    sltu t5,s0,t6
    bne t5,zero,lf_game
    addiu t6,t6,0xB00
    sltu t5,s0,t6
    beq t5,zero,lf_game
    nop
    sw zero,{O_LK2}(t7)
    sw zero,{O_TX2}(t7)
    lui t9,0x0013
    j look_p2
    ori t9,t9,0xD620
lf_game:
    j 0x0013D620
    nop

look_p2:                          # the game's look routine (t9) on player 2's state. a0, a1 = its arguments
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd a0,16(sp)
    sd a1,24(sp)
    sd t9,32(sp)
    lui t7,%hi(CMD_DISPLAY)
    lw s0,%lo(CMD_DISPLAY)(t7)
    beq s0,zero,lp_out            # no display: his frame is made with the next one (look_build reads the note)
    lui t7,0x000F
    lw t6,{O_CSD}(t7)
    bne t6,s0,lp_out              # he has no state with this display yet: the same
    lw t6,{O_BIN}(t7)
    bne t6,zero,lp_out            # (never: these calls come from the heroes' own updates)
    nop
    jal OWN_SWAP
    move a0,s0
    jal look_swap
    move a0,s0
    lui t7,0x000F
    li t6,1
    sw t6,{O_CSW}(t7)             # rows that end or begin now are his
    lw t6,0x2B0(s0)               # the rows' fade value is one for both players (the menu's "revealed" state is
    sd t6,40(sp)                  # player 1's, see own_hud): kept as it is
    ld t9,32(sp)
    ld a0,16(sp)
    jalr t9
    ld a1,24(sp)
    ld t6,40(sp)
    sw t6,0x2B0(s0)
    jal look_swap
    move a0,s0
    jal OWN_SWAP
    move a0,s0
    lui t7,0x000F
    sw zero,{O_CSW}(t7)
lp_out:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,64

look_world:                       # in place of the jump to 0x0013D6B0 at 0x00198A84 (a world's own menu: sheet a0,
    lui t7,0x000F                 # look a1). Player 1's state takes it now; player 2's is made anew in his next run
    sw a0,{O_WTX}(t7)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal OWN_KILLROWS
    nop
    lui t7,0x000F
    sw zero,{O_CSD}(t7)
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    j 0x0013D6B0
    addiu sp,sp,32

look_woff:                        # in place of the call of 0x0013D620 at 0x0013D760 (the world's own menu ends)
    lui t7,0x000F
    j 0x0013D620
    sw zero,{O_WTX}(t7)

look_filter:                      # from own_filter (HUD draw-all), for everything it lets through. a0 = HUD object.
    lui t4,0x000F                 # The holder sends its sheet to the screen memory when it is drawn: in a picture
    lw t5,{O_OBJ2}(t4)            # only the holder of the player whose menu is drawn may do that
    lw t3,{O_BIN}(t4)             # 1 = player 2's state is in the display (his HUD run)
    lw t2,{O_PMODE}(t4)
    addiu t2,t2,-2
    sltiu t2,t2,1                 # 1 = player 2's picture
    bne a0,t5,lfi_h1
    and t3,t3,t2                  # 1 = player 2's own menu is being drawn
    beq t3,zero,lfi_hide          # player 2's holder: only then
    nop
    b lfi_go
    nop
lfi_h1:
    beq t3,zero,lfi_go
    lw t5,{O_H1}(t4)              # the game's holder (noted while player 2's is in)
    bne a0,t5,lfi_go
    nop
lfi_hide:
    lw t7,12(a0)
    ori t7,t7,2
    jr ra
    andi t6,t7,0x40
lfi_go:
    j PV_FILTER
    nop
"""


def add_menu_looks(result, origin, sections, make_v2, elf_word):
    """Step 9 of main(): the command menu's frame and picture sheet per player. Returns the number of words."""
    syms = {}
    for _sec, _title, rows in sections:
        for addr, _w, labels, _src, _c in rows:
            for lab, _lc in labels:
                syms[lab] = addr

    def jal(t):
        return (3 << 26) | ((t >> 2) & 0x3FFFFFF)

    def j(t):
        return (2 << 26) | ((t >> 2) & 0x3FFFFFF)

    def rows(fresh, swap, fgo, more):       # step 7's routines again (same addresses), with three calls re-aimed
        text = ROWS_SRC.format(O_LIVE=make_v2.O_LIVE, O_PMODE=make_v2.O_PMODE, O_CSD=O_CSD, O_CSW=O_CSW, O_SH=O_SH,
                               SH_FE=O_SH + 0xFE - 0x18, SH_FD=O_SH + 0xFD - 0x18, O_POOL2=O_POOL2, O_EFF2=O_EFF2,
                               O_OBJ2=O_OBJ2, FRESH=fresh, SWAP=swap, FGO=fgo)
        sy = {"CMD_DISPLAY": 0x003484A0, "PV_HUD": syms["pv_hud"], "PV_FILTER": syms["pv_filter"], "PV_UFILTER": syms["pv_ufilter"]}
        sy.update(more)
        rcode, labels = assemble(ROWS_AT, text, sy)
        return [w if isinstance(w, int) else w[1] for w in rcode], labels

    old_code, rl = rows("own_fresh", "own_swap", "PV_FILTER", {})
    for i, w in enumerate(old_code):
        assert result.get(ROWS_AT + 4 * i) == w, "step 7's routines are not the ones in the patch"
    src = LOOK_SRC.replace("@LOOKHIDE@", LOOK_PLAIN if "--no-lookhide" in sys.argv else LOOK_HIDE).format(O_LK2=O_LK2, O_TX2=O_TX2, O_WTX=O_WTX, O_BIN=O_BIN, O_H1=O_H1, O_B=O_B, O_B4=O_B + 4, O_B8=O_B + 8,
                          O_OBJ2=O_OBJ2, O_CSD=O_CSD, O_CSW=O_CSW, O_PMODE=make_v2.O_PMODE)
    code, ll = assemble(LOOK_AT, src, {"CMD_DISPLAY": 0x003484A0, "PV_FILTER": syms["pv_filter"], "OWN_SWAP": rl["own_swap"],
                                       "OWN_FRESH": rl["own_fresh"], "OWN_KILLROWS": rl["own_killrows"]})
    code = [w if isinstance(w, int) else w[1] for w in code]
    assert LOOK_AT + 4 * len(code) <= LOOK_END, "menu look routines too long (%d words)" % len(code)
    for i, w in enumerate(code):
        a = LOOK_AT + 4 * i
        assert a not in result, "address already used: %08X" % a
        result[a] = w
        origin[a] = "glue (command menu frame and sheet per player)"
    for a in range(0x000F0000 + O_LK2, LOOK_DATA_END, 4):
        assert a not in result, "data address written by the patch: %08X" % a
    new_code, rl2 = rows("LOOK_FRESH2", "OWN_SWAP2", "LOOK_FILTER", {"LOOK_FRESH2": ll["look_fresh2"],
                                                                     "OWN_SWAP2": ll["own_swap2"], "LOOK_FILTER": ll["look_filter"]})
    assert all(rl2[k] == v for k, v in rl.items()) and len(new_code) == len(old_code), "step 7's routines moved"
    changed = 0
    for i, w in enumerate(new_code):
        a = ROWS_AT + 4 * i
        if result[a] != w:
            result[a] = w
            origin[a] = "glue (command menu rows per player; re-aimed by the frame and sheet step)"
            changed += 1
    assert changed == 4, "expected four re-aimed words in step 7's routines, found %d" % changed
    # the display no longer ends player 2's rows when player 1's menu changes its look (each has his own now)
    assert result.get(0x0013D4C8) == j(rl["own_d4c8"]), "hook 0x0013D4C8 is not step 7's"
    del result[0x0013D4C8]
    del origin[0x0013D4C8]
    hooks = ((0x0013B274, jal(0x0013B1D0), jal(ll["look_hold"]), "a new display: both holders become HUD objects"),
             (0x0013B41C, jal(0x0013B1D0), jal(ll["look_hold"]), "a HUD restart: both holders again"),
             (0x001D4840, jal(0x0013D550), jal(ll["look_on"]), "a board menu opens: the look of that player's menu only"),
             (0x001D48C8, jal(0x0013D620), jal(ll["look_off"]), "a board menu closes: that player's menu only"),
             (0x0013D760, jal(0x0013D620), jal(ll["look_woff"]), "the world's own menu ends"),
             (0x00198A84, j(0x0013D6B0), j(ll["look_world"]), "a world's own menu: for both players"))
    for a, orig, new, what in hooks:
        assert a not in result, "hook address already used: %08X" % a
        assert elf_word(a) == orig, "hook %08X: program has %08X, expected %08X" % (a, elf_word(a) or 0, orig)
        result[a] = new
        origin[a] = "glue hook (command menu frame and sheet per player): %s" % what
    return len(code) + len(hooks)


def add_boss_views(result, origin, elf_word=None):
    """Step 8: the routines the camera task of tools/own/views.py calls (BM_HOLD, BM_CAM1, BM_CAM2)."""
    src = BOSSV_SRC
    if "--cannon1view" in sys.argv:                 # (eighth round, experiment) the toy cannon: one view for both cannons
        x = """    beq t8,zero,bw_one            # no twin in this room
    lui t2,0x0034
"""
        assert src.count(x) == 1
        src = src.replace(x, x + """    lui t4,0x0035
    lw t9,-5816(t4)               # the engine's player
    beq t9,zero,bw_c1
    nop
    lw t6,8(t9)
    lw t6,0(t6)                   # his object number
    li t0,0x03C8
    beq t6,t0,bw_one              # a toy cannon: one view, both cannons seen from behind
    nop
bw_c1:
""")
    syms8 = {}
    if "--cannon2view" in sys.argv:                 # (ninth round, job 5) the toy cannon: a view for each player
        assert "--cannon1view" not in sys.argv, "--cannon2view takes the place of --cannon1view"
        cn_code, cn_labels = assemble(CN_AT, CN_SRC, {})
        cn_code = [w if isinstance(w, int) else w[1] for w in cn_code]
        assert CN_AT + 4 * len(cn_code) <= CN_END, "the toy cannon's camera: too long (%d words)" % len(cn_code)
        for i, w in enumerate(cn_code):
            assert CN_AT + 4 * i not in result, "the toy cannon's camera: address already used %08X" % (CN_AT + 4 * i)
            result[CN_AT + 4 * i] = w
            origin[CN_AT + 4 * i] = "own screens step 8 (the toy cannon's view for each player)"
        syms8["CN_VIEW"] = cn_labels["cn_view"]
        x = """bm_cam2:                          # camera 2's update (a0 = the camera, a1 = 0; player 2's camera is swapped in)
    lui t7,0x000F
"""
        assert src.count(x) == 1
        src = src.replace(x, x + """    lw t9,0x05CC(t7)              # the twin
    beq t9,zero,b2_k9
    nop
    lw t6,8(t9)
    lw t6,0(t6)                   # his object number
    xori t6,t6,0x03C8
    bne t6,zero,b2_k9
    nop
    j CN_VIEW                     # a toy cannon: camera 2 = camera 1's still view, moved to his cannon
    nop
b2_k9:
""")
    code, _labels = assemble(BOSSV_AT, src, syms8)
    code = [w if isinstance(w, int) else w[1] for w in code]
    assert BOSSV_AT + 4 * len(code) <= BOSSV_END, "boss views: too long (%d words)" % len(code)
    for i, w in enumerate(code):
        a = BOSSV_AT + 4 * i
        assert a not in result, "boss views: address already used %08X" % a
        result[a] = w
        origin[a] = "own screens step 8 (a boss's scripted move keeps two views)"
    return len(code)


def add_menu_rows(result, origin, sections, make_v2, elf_word):
    """Step 7 of main(): the command menu's rows per player. Returns the number of words added or changed."""
    syms = {}
    for _sec, _title, rows in sections:
        for addr, _w, labels, _src, _c in rows:
            for lab, _lc in labels:
                syms[lab] = addr
    pv_hud, pv_filter, pv_ufilter = syms["pv_hud"], syms["pv_filter"], syms["pv_ufilter"]

    def jal(t):
        return (3 << 26) | ((t >> 2) & 0x3FFFFFF)

    def j(t):
        return (2 << 26) | ((t >> 2) & 0x3FFFFFF)

    src = ROWS_SRC.format(O_LIVE=make_v2.O_LIVE, O_PMODE=make_v2.O_PMODE, O_CSD=O_CSD, O_CSW=O_CSW, O_SH=O_SH,
                          SH_FE=O_SH + 0xFE - 0x18, SH_FD=O_SH + 0xFD - 0x18, O_POOL2=O_POOL2, O_EFF2=O_EFF2, O_OBJ2=O_OBJ2,
                          FRESH="own_fresh", SWAP="own_swap", FGO="PV_FILTER")
    code, labels = assemble(ROWS_AT, src, {"CMD_DISPLAY": 0x003484A0, "PV_HUD": pv_hud, "PV_FILTER": pv_filter,
                                           "PV_UFILTER": pv_ufilter})
    code = [w if isinstance(w, int) else w[1] for w in code]
    assert ROWS_AT + 4 * len(code) <= ROWS_END, "menu row routines too long"
    for i, w in enumerate(code):
        a = ROWS_AT + 4 * i
        assert a not in result, "address already used: %08X" % a
        result[a] = w
        origin[a] = "glue (command menu rows per player)"
    for a in range(0x000F0000 + O_CSD, ROWS_DATA_END, 4):
        assert a not in result, "data address written by the patch: %08X" % a
    n = len(code)
    # lane V2's hooks and calls that now go through the new routines
    calls = [a for a, w in result.items() if w == jal(pv_hud) and 0x000F0000 <= a < 0x000F8000 and not ROWS_AT <= a < ROWS_END]
    assert len(calls) == 2, "expected two calls of pv_hud, found %d" % len(calls)
    for a in calls:
        result[a] = jal(labels["own_hud"])
        origin[a] = "glue (command menu rows per player; was lane V2: jal pv_hud)"
    for a, old, new, what in ((0x0013921C, jal(pv_ufilter), jal(labels["own_ufilter"]), "HUD object's task"),
                              (0x0013935C, jal(pv_filter), jal(labels["own_filter"]), "HUD draw-all")):
        assert result.get(a) == old, "hook %08X is not lane V2's" % a
        result[a] = new
        origin[a] = "glue (command menu rows per player, %s; then lane V2's routine)" % what
    # new hooks in the game program
    for a, orig, new, what in ((0x0013B128, 0x240FFFFF, j(labels["own_forget"]), "the display forgets its rows"),
                               (0x0013D4C8, 0x27BDFFF0, j(labels["own_d4c8"]), "the display removes all its rows"),
                               (0x0013B498, 0xAE0084A0, jal(labels["own_gone"]), "the display object ends"),
                               (0x0013B394, 0x0C04EB48, jal(labels["own_pools"]), "a new display gets its pools: twice, one set is player 2's"),
                               (0x0013B474, 0x0C04EBB6, jal(labels["own_unpools"]), "the display's pools are freed: both sets"),
                               (0x0013ACC0, 0x8DF08058, j(labels["own_alloc"]), "a new row is taken: from the pool of the player whose menu is being built"),
                               (0x0013AB28, 0x8DEC8058, j(labels["own_rel"]), "a row goes back: to the pool it came from")):
        assert a not in result, "hook address already used: %08X" % a
        assert elf_word(a) == orig, "hook %08X: program has %08X, expected %08X" % (a, elf_word(a) or 0, orig)
        result[a] = new
        origin[a] = "glue hook (command menu rows per player): %s" % what
    return n + 11


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base_name = "merged-v6"
    if "--base" in sys.argv:
        base_name = sys.argv[sys.argv.index("--base") + 1]
        args.remove(base_name)
    out = ROOT / (args[0] if args else "patches/merged-v6-own")
    perview = "--no-perview" not in sys.argv

    # 1. OWN = merged-v2 + lane V1 (current generator) + lane V2
    park = "--plain" not in sys.argv and "--nopark" not in sys.argv      # (use the fork tools/own/views.py)
    if park:
        make_v1 = load_module("own_views", ROOT / "tools" / "own" / "views.py")
    else:
        make_v1 = load_module("make_v1", ROOT / "tools" / "lane-v1" / "make_v1.py")
    sys.modules["v1_views"] = make_v1          # lane V2's generator imports its snapshot under this name
    make_v2 = load_module("make_v2", ROOT / "tools" / "lane-v2" / "make_v2.py")
    if park:
        vopts = {a[7:] for a in sys.argv if a.startswith("--vopt=")}      # experiments: options of tools/own/views.py
        if vopts:
            _real_build = make_v1.build
            make_v1.build = lambda _opts: _real_build(set(vopts))
        _s, _h, vsyms = make_v1.build(set())
        # lane V2's task hook at priority 90000 draws player 1's HUD and then jumps to "BUF_SWITCH" (the game's
        # capture): in park mode it jumps to v_park, which parks the picture (or calls the capture for the game's
        # own cross-fade)
        for name in ("v_keep", "v_park"):       # (neither with --vopt=nopark)
            if name in vsyms:
                make_v2.SYM["BUF_SWITCH"] = vsyms[name]
    names = {"views", "p2gauge"} | ({"perview"} if perview else set())
    sections, hooks = make_v2.build(names)
    elf_word = make_v2.M.load_elf_words()
    own, meaning = {}, {}
    for sec, title, rows in sections:
        for addr, w, _labels, _src, comment in rows:
            assert addr not in own, "code address twice: %08X" % addr
            assert elf_word(addr) is None, "code address inside the game program: %08X" % addr
            own[addr] = w
            meaning[addr] = "own screens, section %s" % sec
    for addr, w, orig, sec, what in hooks:
        assert addr not in own, "hook address twice: %08X" % addr
        have = elf_word(addr)
        assert have is not None, "hook outside the game program: %08X" % addr
        assert orig is None or have == orig, "hook %08X: program has %08X, expected %08X" % (addr, have, orig)
        own[addr] = w
        meaning[addr] = "own screens, hook of section %s: %s" % (sec, what)

    # 2. - 4. the merged build's own additions on top
    _, a_words = load_patch("lane-v2-p2gauge")
    base_order, base = load_patch(base_name)
    base_origin = load_listing(base_name)
    for a, w in a_words.items():
        if a in REAIMED:
            continue
        if own.get(a) != w:
            raise SystemExit("OWN differs from lane V2's gauge-alone form at %08X: %s / %08X"
                             % (a, "%08X" % own[a] if a in own else "missing", w))
    new_in_own = {a for a in own if a not in a_words} | REAIMED
    delta_set = {a: w for a, w in base.items() if a_words.get(a) != w}
    delta_del = [a for a in a_words if a not in base]
    clash = sorted(a for a in list(delta_set) + delta_del if a in new_in_own)
    if clash:
        raise SystemExit("the merged build and the own-screen sections both write: " + ", ".join("%08X" % a for a in clash))
    result = dict(own)
    origin = dict(meaning)
    for a in delta_del:
        result.pop(a, None)
        origin.pop(a, None)
    for a, w in delta_set.items():
        result[a] = w
        origin[a] = base_origin.get(a, base_name)
    for a in result:
        if a not in origin or (a in a_words and a not in delta_set and a not in REAIMED and not origin[a].startswith("own")):
            origin[a] = base_origin.get(a, base_name)
    for a in a_words:
        if a in result and a not in delta_set and a not in REAIMED:
            origin[a] = base_origin.get(a, "merged-v2")

    # 5. the ring rule (merged build 5) for the second small gauge: player 1's hero in player 2's picture
    n_glue = 0
    if perview and base.get(0x000F7004) == 0x000F3440:
        syms = {}
        for sec, title, rows in sections:
            for addr, w, labels, _src, _c in rows:
                for lab, _lc in labels:
                    syms[lab] = addr
        tg2_class = syms["tg2_class"]
        tg2_update = syms["tg2_update"]
        assert result[tg2_class + 4] == tg2_update, "tg2_class word 1 is not tg2_update"
        src = """
        tg2_rings:                    # class method "update" of the small gauge of player 1's hero. a0 = gauge
            addiu sp,sp,-16
            sd ra,0(sp)
            sd s0,8(sp)
            jal TG2_UPDATE
            move s0,a0
            j RINGS_COMMON            # the rest is merged build 5's ring routine (same stack frame)
            nop
        """
        code, _ = assemble(RINGS2_AT, src, {"TG2_UPDATE": tg2_update, "RINGS_COMMON": RINGS_COMMON})
        code = [w if isinstance(w, int) else w[1] for w in code]
        # the common part must be where merged build 5 has it: "lw t7,0x34(s0)" right after the delay slot of its jal
        assert result.get(RINGS_COMMON) == 0x8E0F0034 and result.get(RINGS_COMMON - 4) == 0x0080802D, "ring routine moved"
        for i, w in enumerate(code):
            a = RINGS2_AT + 4 * i
            assert a not in result, "glue address already used: %08X" % a
            result[a] = w
            origin[a] = "glue (ring rule for the small gauge of player 1's hero in player 2's picture)"
        result[tg2_class + 4] = RINGS2_AT
        origin[tg2_class + 4] = "glue (was lane V2: update method %08X)" % tg2_update
        n_glue = len(code)

        # 6. the same rule for player 2's own BIG gauge (a second object of the game's player gauge class).
        # The game hides the parts of player 1's gauge when it builds it (hero's slot flag bit 1); lane V2's
        # second gauge is built before it has its character, so the game's rule does not reach it.
        # Which parts: the 13 embedded parts whose "hidden" flag differs between the first town and a normal room
        # in player 1's gauge (VERIFIED by the memory probe, tests g1-town / g1-roam). A HUD is built anew in
        # every room, so the parts are only ever hidden here, never shown again.
        pg_class = syms["pg_class"]
        pg_update = syms["pg_update"]
        assert result[pg_class + 4] == pg_update, "pg_class word 1 is not pg_update"
        pg_at = 0x000F7240          # lane V2's marker area, free since the 1P/2P markers were taken out
        parts = [0x0394, 0x1BCC, 0x1D68, 0x1F04, 0x2574, 0x2710, 0x28AC, 0x2A48, 0x2BE4, 0x2D80, 0x2F1C, 0x30B8, 0x33B0]
        src = """
        pg_rings:                     # class method "update" of player 2's own big gauge. a0 = gauge
@PGGUARD@            addiu sp,sp,-16
            sd ra,0(sp)
            sd s0,8(sp)
            jal PG_UPDATE             # lane V2's update (the game's player gauge update for the twin)
            move s0,a0
@GLINT@            lui t7,%hi(PARTY)
            lw t7,%lo(PARTY)(t7)      # player 1's hero
            beq t7,zero,pr_done
            nop
            lw t6,0x48C(t7)           # his unit slot
            beq t6,zero,pr_done
            nop
            lw t6,0x250(t6)           # slot flags: bit 1 = the game hides the player gauge's rings
            andi t6,t6,2
            beq t6,zero,pr_done
            lui t5,%hi(pr_table)
            addiu t5,t5,%lo(pr_table)
            li t4,{n}
        pr_loop:
            lhu t3,0(t5)              # offset of an embedded part
            addu t3,t3,s0
            lw t2,12(t3)              # its flag word
            ori t2,t2,0x40            # hidden
            sw t2,12(t3)
            addiu t4,t4,-1
            bne t4,zero,pr_loop
            addiu t5,t5,2
        pr_done:
            ld ra,0(sp)
            ld s0,8(sp)
            jr ra
            addiu sp,sp,16
        pr_table:
        """.format(n=len(parts)).replace("@GLINT@", "" if "--no-glint" in sys.argv else PG_GLINT)
        src = src.replace("@PGGUARD@", "" if "--no-pgguard" in sys.argv else PG_GUARD)
        padded = parts + [0] * (len(parts) % 2)
        for i in range(0, len(padded), 2):
            src += "            .word 0x%08X\n" % (padded[i] | (padded[i + 1] << 16))
        code2, _ = assemble(pg_at, src, {"PG_UPDATE": pg_update, "PARTY": 0x00348638})
        code2 = [w if isinstance(w, int) else w[1] for w in code2]
        assert pg_at + 4 * len(code2) <= 0x000F7500, "glue too long"
        for i, w in enumerate(code2):
            a = pg_at + 4 * i
            assert a not in result, "glue address already used: %08X" % a
            result[a] = w
            origin[a] = "glue (ring rule for player 2's own big gauge)"
        result[pg_class + 4] = pg_at
        origin[pg_class + 4] = "glue (was lane V2: update method %08X)" % pg_update
        n_glue += len(code2)

    # 7. THE COMMAND MENU'S ROWS PER PLAYER (fault "the Magic list shows on the other player's screen").
    # The game has ONE command menu display object; lane V2 points it at player 2's control object for player 2's
    # HUD run. Its rows (the list entries on screen) sit in a table inside it (+0x18, 4 levels x 9 rows) and its
    # update removes every row the bound control object does not want. With one table for two players the rows of
    # an opened list were removed in the other player's run and made again in the owner's run, in every step.
    # Now player 2 has his own copy of the display's row table and list state (+0x18..+0x103), swapped in around
    # his HUD run; his rows carry a mark (flag bit 30) and are updated and drawn in his picture only.
    n_rows = 0
    if perview and "--no-rows" not in sys.argv:
        n_rows = add_menu_rows(result, origin, sections, make_v2, elf_word)

    # 9. THE COMMAND MENU'S FRAME AND PICTURE SHEET PER PLAYER (fault "one player on a skateboard, the other on
    # foot: the walking player's menu is drawn with the board menu's frame"). The display has ONE frame object
    # (display+0x104, a HUD object of its own) and ONE layout holder (0x00348050) whose picture sheet is sent to the
    # screen memory every time the holder is drawn. A board menu (0x0013D550 / 0x0013D620) and a world's own menu
    # (0x0013D6B0) change both, for whoever asks. Now player 2 has his own copy of the frame's state (flag word,
    # sequence player, board look), swapped in with his rows, and his own holder (step 7 made one and never used
    # it) is a HUD object with its own sheet; in a picture only the holder of that picture's player is drawn.
    # A board menu changes the look of the menu of the player who rides; a world's menu changes both.
    n_looks = 0
    if n_rows and "--no-looks" not in sys.argv:
        n_looks = add_menu_looks(result, origin, sections, make_v2, elf_word)

    # 8. A BOSS'S SCRIPTED MOVE KEEPS TWO VIEWS (tools/own/edit_boss_views.py has the story). The camera task of
    # tools/own/views.py calls three routines here unless the fork was made with --no-bossviews.
    if "--no-bossviews" not in sys.argv and park:
        add_boss_views(result, origin, elf_word)

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, OWN SCREENS: %s + two full-size views (lane V1%s) + a HUD per player (lane V2)."
        % (base_name, "" if not park else ", with markers for the own-view emulator"),
        "comment=Needs the own-view emulator build and the .view file; any other emulator shows player 1's picture.",
        "comment=Every PC in an online game must have this same file.",
    ]
    order = sorted(result)
    (out / NAME).write_text("\n".join(head + ["patch=1,EE,%08X,word,%08X" % (a, result[a]) for a in order]) + "\n", encoding="utf-8")
    (out / "listing.txt").write_text("\n".join("%08X %08X  %s" % (a, result[a], origin.get(a, "?")) for a in order) + "\n", encoding="utf-8")
    counts = {}
    for a in order:
        k = origin.get(a, "?").split(":")[0].split(" (")[0]
        counts[k] = counts.get(k, 0) + 1
    print("OWN (merged-v2 + V1 + V2): %d words; merged build delta: %d set, %d removed; ring glue: %d; menu rows per player: %d; menu frame and sheet per player: %d"
          % (len(own), len(delta_set), len(delta_del), n_glue, n_rows, n_looks))
    for k in sorted(counts):
        print("  %5d  %s" % (counts[k], k))
    print("written: %s (%d words), sha1 %s" % (out / NAME, len(order), hashlib.sha1((out / NAME).read_bytes()).hexdigest()))


if __name__ == "__main__":
    main()
