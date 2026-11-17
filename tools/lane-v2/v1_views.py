"""Lane V1: two-view mode (own screen per player) on the merged build. CRC F266B00B, KH2 Final Mix SLPM-66675.

  python -I tools/lane-v1/make_v1.py [outDir] [options...]

Default outDir: patches/lane-v1-two-views. Output: SLPM-66675_F266B00B.pnach and listing.txt.
The patch = every word of merged build v2 (tools/merge/make_all.py --v2, imported, not edited) + SECTION views.

Options (for experiments and control runs):
  noviews     merged-v2 only (control: must equal patches/merged-v2 word for word)
  nomove      leave out the movement hook (the twin's stick is then turned by camera 1)
  nostick     the camera code always reads controller 1 (camera 2 then turns with pad 1)
  nohold      do not fall back to one view while an event holds the camera
  nolock      leave out the four lock-on hooks (player 2's lock-on then acts on camera 1, as in merged-v2)
  stack       views one above the other instead of side by side (experiment)
  noexits     TEST ONLY: leave out lane E's exit rule, so player 1 alone triggers exits and events

THE CONTRACT (see docs/lanes/V1-two-views.md):
  0x000F6F00  byte  VIEW LAYOUT of the picture most recently sent to the graphics chip
                    0 = one full view   1 = two views side by side: LEFT half = player 2, RIGHT half = player 1
  0x000F6F01  byte  layout of the picture being built in the current step (becomes 0x000F6F00 when it is sent)
  0x000F6F04  word  1 while the two-view render tasks installed in the scene are OURS
  0x000F6F08  word  switch request waiting for the end of the step (1 = to two views, 2 = to one view)
  0x000F6F0C  word  not 0 while player 2's camera is swapped into the game's camera memory
  0x000F6E00        player 2's camera object while it is NOT swapped in (0xF0 bytes, layout of 0x00348710)
  0x000F6C00        player 2's copy of the camera module's variables 0x0034A970-0x0034AA8F (0x120 bytes)

How player 2 gets a camera of the game's own kind: the camera code addresses "the camera" (0x00348710) and its
type variables (0x0034A970-0x0034AA8F) directly in many places. Instead of changing those places, the patch SWAPS
the contents of that memory with player 2's copies around every piece of camera work done for player 2 (camera 2's
update, and the lock-on calls of player 2's lock-on manager), and swaps back afterwards.

Memory: routines 0x000F6000.. (must end before 0x000F6C00), data 0x000F6C00-0x000F6FFF.
Lane K's old demo cave 0x000F0E00-0x000F0FFF is NOT used.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import make_all  # noqa: E402
import mips  # noqa: E402

VIEWS_AT = 0x000F6000
VIEWS_END = 0x000F6C00

VSYM = {
    # game routines
    "CAM_UPDATE": 0x00140B68,     # camera update (camera, flag); writes the result into the current view's block
    "CAM_INIT": 0x0013F558,       # camera reset from its target
    "LOCK_CAM": 0x0015A638,       # lock-on manager -> camera: go into lock-on mode (a0 = manager + 4)
    "SET_VIEW": 0x001069F8,       # choose the current view index (0 or 1)
    "GET_VIEW": 0x00106A60,       # view block getter
    "SINGLE_OFF": 0x001619E8,     # remove the one-view render tasks (task group 3)
    "SINGLE_ON": 0x001618F0,      # install the one-view render tasks
    "DUAL_ON": 0x001620A8,        # install the game's two-view render tasks (task group 5)
    "DUAL_OFF": 0x001623B0,       # remove the two-view render tasks (hooked: v_dualoff)
    "DUAL_OFF_BODY": 0x001623B8,  # ... its third instruction
    "COMPOSE": 0x00161AA8,        # put the two view pictures on the screen (blended; used by the game's cross-fades)
    "SEND": 0x0014E5F0,           # end of step: send the finished draw list to the graphics chip
    "TASK_ADD": 0x00102C18,       # add a task (group, priority, routine) to the current scene
    "TASK_END": 0x001024A8,       # a task removes itself
    "TASKS_OF": 0x00102C80,       # current scene's task owner
    "TASK_REMOVE_GROUP": 0x00102688,
    "SPR_INIT": 0x0014C050, "ATEXIT": 0x002FD188,
    "SPR_SETA": 0x0014B5E0, "SPR_SETB": 0x0014B630, "SPR_SIZE": 0x0014B208, "SPR_UV": 0x0014B5E8,
    "SPR_TEX": 0x0014B628, "SPR_COLOR": 0x0014B220, "SPR_DRAW": 0x0014C350, "SPR_MID": 0x0014E098,
    # game data
    "CAM1": 0x00348710,           # the game's camera (0xF0 bytes; type +0x40, target object +0x44)
    "CAM1_TYPE": 0x00348750,
    "CAM1_TARGET": 0x00348754,
    "CAMG": 0x0034A970,           # the camera module's own variables, 0x0034A970-0x0034AA8F
    "DUAL_FLAG": 0x0033CC44,      # byte: 1 while two-view render tasks are installed
    "CAM_HOLD": 0x0033CC38,       # not 0 while an event holds the camera (the camera task then does nothing)
    "SPR_A": 0x004F3B60,          # sprite of view picture A (view 1)
    "SPR_B": 0x004F3E70,          # sprite of view picture B (view 0)
    "SPR_B_X": 0x004F3E78,        # its x position (16-bit; y at +2)
    "S2_STICK": 0x000F1A30,       # stick copy inside the second control object S2 (lane G): the twin's stick
    "PAD1_STICK": 0x0034D750,     # stick inside logical controller 2
    # our data (zero at boot, never written by the patch file)
    "V_CG2": 0x000F6C00,
    "V_CAM2": 0x000F6E00,
    "V_SHOWN": 0x000F6F00,
    "V_PENDING": 0x000F6F01,
    "V_ON": 0x000F6F04,
    "V_REQ": 0x000F6F08,
    "V_DEPTH": 0x000F6F0C,
}

# offsets from 0x000F0000 (a register holds 0x000F0000)
O = dict(O_TWIN=0x05CC, O_S2=0x1000, O_S2MGR=0x1AC0, O_S2MGR4=0x1AC4, O_CG2=0x6C00, O_CAM2=0x6E00, O_CAM2T=0x6E44,
         O_SHOWN=0x6F00, O_PENDING=0x6F01, O_ON=0x6F04, O_REQ=0x6F08, O_DEPTH=0x6F0C)

VIEWS_SRC = """
v_camtask:                        # replaces the body of the camera task 0x00140CC8 (priority 26000, every step)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui a0,%hi(CAM1)
    addiu a0,a0,%lo(CAM1)
    jal CAM_UPDATE                # camera 1 exactly as the game does it (writes view 0)
    move a1,zero
    lui s0,0x000F
    lw t0,{O_ON}(s0)
    beq t0,zero,v_c_want
    nop
    jal v_enter                   # two views are on: put player 2's camera into the game's camera memory
    nop
    lw t1,{O_TWIN}(s0)
    lui t2,%hi(CAM1_TARGET)
    sw t1,%lo(CAM1_TARGET)(t2)    # it follows the twin (target 0 = the update does nothing)
    jal SET_VIEW                  # view index 1 while it updates
    li a0,1
    lui a0,%hi(CAM1)
    addiu a0,a0,%lo(CAM1)
    jal CAM_UPDATE                # camera 2 through the game's own update (writes view 1)
    move a1,zero
    jal SET_VIEW
    move a0,zero
    jal v_leave                   # put player 1's camera back
    nop
v_c_want:                         # do we want two views in the next step?
    lw t1,{O_TWIN}(s0)
    beq t1,zero,v_c_no            # no twin in this room
    lui t2,%hi(CAM_HOLD)
    lw t3,%lo(CAM_HOLD)(t2)
    {hold_branch}                 # an event holds the camera: one full view
    nop
    lw t0,{O_ON}(s0)
    bne t0,zero,v_c_done          # already on
    li t4,1
    b v_c_req                     # ask for the switch to two views
    nop
v_c_no:
    lw t0,{O_ON}(s0)
    beq t0,zero,v_c_done          # already off
    li t4,2                       # ask for the switch back to one view
v_c_req:
    lw t5,{O_REQ}(s0)
    bne t5,zero,v_c_done          # a switch is already waiting
    lui a2,%hi(v_switch)
    sw t4,{O_REQ}(s0)
    addiu a2,a2,%lo(v_switch)
    lui a1,0x0001
    ori a1,a1,0x86A1              # priority 100001: after every draw task, just after the game's own fade starter
    jal TASK_ADD                  # one-shot task: the switch happens at the end of this step, like the game's own
    li a0,1
v_c_done:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32

v_switch:                         # one-shot task at the end of a step. a0 = this task
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd a0,16(sp)
    lui s0,0x000F
    lw t4,{O_REQ}(s0)
    sw zero,{O_REQ}(s0)
    li t5,1
    bne t4,t5,v_s_off
    lw t0,{O_ON}(s0)
    bne t0,zero,v_s_end           # already ours
    lui t1,%hi(DUAL_FLAG)
    lbu t2,%lo(DUAL_FLAG)(t1)
    bne t2,zero,v_s_end           # the game's own two-view cross-fade is running: hands off
    lw t3,{O_TWIN}(s0)
    beq t3,zero,v_s_end           # the twin went away meanwhile
    nop
    jal SINGLE_OFF                # remove the one-view draw tasks
    nop
    jal DUAL_ON                   # install the game's two-view draw tasks
    nop
    li t0,1
    sw t0,{O_ON}(s0)
    lui a0,%hi(CAM1)              # player 2's camera starts as a copy of player 1's camera ...
    addiu a0,a0,%lo(CAM1)
    addiu a1,s0,{O_CAM2}
    jal v_copy
    addiu a2,a0,0xF0
    lui a0,%hi(CAMG)              # ... and of the camera module's variables
    addiu a0,a0,%lo(CAMG)
    addiu a1,s0,{O_CG2}
    jal v_copy
    addiu a2,a0,0x120
    jal v_enter
    nop
    lw t0,{O_TWIN}(s0)
    lui t2,%hi(CAM1_TARGET)
    sw t0,%lo(CAM1_TARGET)(t2)    # its target is the twin
    lui t2,%hi(CAM1_TYPE)
    lw t3,%lo(CAM1_TYPE)(t2)
    li t4,2
    bne t3,t4,v_s_i1
    nop
    sw zero,%lo(CAM1_TYPE)(t2)    # player 1's lock-on is not player 2's: plain follow camera
v_s_i1:
    lui a0,%hi(CAM1)
    jal CAM_INIT                  # reset behind the twin by the game's own routine (also clears the lock-on flag)
    addiu a0,a0,%lo(CAM1)
    lw t0,{O_S2}(s0)              # player 2's control object S2 (lane G); first word 0 until it is built
    beq t0,zero,v_s_i2
    lw t1,{O_S2MGR}(s0)           # state of player 2's lock-on manager
    li t2,2
    bne t1,t2,v_s_i2
    nop
    jal LOCK_CAM                  # player 2 is locked on: its camera goes into lock-on mode
    addiu a0,s0,{O_S2MGR4}
v_s_i2:
    jal v_leave
    nop
    b v_s_end
    nop
v_s_off:
    lw t0,{O_ON}(s0)
    beq t0,zero,v_s_end
    nop
    jal DUAL_OFF                  # hooked (v_dualoff): removes our two-view tasks and puts the one-view tasks back
    nop
v_s_end:
    ld a0,16(sp)
    ld ra,0(sp)
    ld s0,8(sp)
    j TASK_END                    # the task removes itself
    addiu sp,sp,32

v_copy:                           # a0 = from, a1 = to, a2 = end of from
    lw t0,0(a0)
    addiu a0,a0,4
    sw t0,0(a1)
    bne a0,a2,v_copy
    addiu a1,a1,4
    jr ra
    nop

v_enter:                          # player 2's camera into the game's camera memory (nesting is counted)
    lui t7,0x000F
    lw t6,{O_DEPTH}(t7)
    addiu t6,t6,1
    sw t6,{O_DEPTH}(t7)
    li t5,1
    beq t6,t5,v_swapall
    nop
    jr ra
    nop
v_leave:                          # and player 1's camera back
    lui t7,0x000F
    lw t6,{O_DEPTH}(t7)
    addiu t6,t6,-1
    sw t6,{O_DEPTH}(t7)
    beq t6,zero,v_swapall
    nop
    jr ra
    nop
v_swapall:                        # exchange the camera object and the camera module's variables with player 2's copies
    lui a0,%hi(CAM1)
    addiu a0,a0,%lo(CAM1)
    lui a1,0x000F
    addiu a1,a1,{O_CAM2}
    addiu a2,a0,0xF0
v_sw1:
    lw t0,0(a0)
    lw t1,0(a1)
    sw t1,0(a0)
    sw t0,0(a1)
    addiu a0,a0,4
    bne a0,a2,v_sw1
    addiu a1,a1,4
    lui a0,%hi(CAMG)
    addiu a0,a0,%lo(CAMG)
    lui a1,0x000F
    addiu a1,a1,{O_CG2}
    addiu a2,a0,0x120
v_sw2:
    lw t0,0(a0)
    lw t1,0(a1)
    sw t1,0(a0)
    sw t0,0(a1)
    addiu a0,a0,4
    bne a0,a2,v_sw2
    addiu a1,a1,4
    jr ra
    nop

v_w_unlock:                       # hook 0x0019CC58 (was: jal 0x0019D480). s0 = the lock-on manager that lets go
    lui t9,%hi(0x0019D480)
    b v_wrap
    addiu t9,t9,%lo(0x0019D480)
v_w_lock:                         # hook 0x0019CB00 (was: jal 0x0019D438). s0 = the lock-on manager that locks on
    lui t9,%hi(0x0019D438)
    b v_wrap
    addiu t9,t9,%lo(0x0019D438)
v_w_att:                          # hook 0x0019CA04 (was: jal 0x0015A638). s0 = lock-on manager at attach time
    lui t9,%hi(0x0015A638)
    b v_wrap
    addiu t9,t9,%lo(0x0015A638)
v_w_tgt:                          # hook 0x0019D09C (was: jal 0x0015A6C8). s0 = lock-on manager updating its target
    lui t9,%hi(0x0015A6C8)
    addiu t9,t9,%lo(0x0015A6C8)
v_wrap:                           # s0 = lock-on manager, t9 = the game's routine, a0-a3 = its arguments
    lui t0,0x000F
    addiu t0,t0,{O_S2MGR}
    beq s0,t0,v_wrap2
    nop
    jr t9                         # player 1's manager: the game's own call, camera 1
    nop
v_wrap2:                          # player 2's manager (inside S2): the same call with player 2's camera in place
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    sd t9,40(sp)
    jal v_enter
    nop
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,32(sp)
    ld t9,40(sp)
    jalr t9
    nop
    sd v0,8(sp)
    jal v_leave
    nop
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,64

v_pad:                            # the camera code's eight controller reads (were: jal GET_PAD with index 0)
    lui t0,0x000F
    lw t1,{O_DEPTH}(t0)
    j GET_PAD
    {pad_index}                   # controller 2 while player 2's camera is in place, else controller 1

v_view:                           # hook 0x0017837C inside "stick -> world direction" (was: jal GET_VIEW, a0 = 1)
    lui t0,0x000F                 # s1 = the stick being turned
    lw t1,{O_ON}(t0)
    beq t1,zero,v_v_cur           # one view: everybody moves relative to camera 1
    lui t2,%hi(S2_STICK)
    addiu t2,t2,%lo(S2_STICK)
    beq s1,t2,v_v_one             # the stick copy of the twin's control object S2
    lui t2,%hi(PAD1_STICK)
    addiu t2,t2,%lo(PAD1_STICK)
    bne s1,t2,v_v_cur             # the stick of controller 2 itself
    nop
v_v_one:
    lui v0,0x003A
    jr ra
    ori v0,v0,0x8000              # view 1's block (camera 2): 0x003A7F70 + 0x90
v_v_cur:
    j GET_VIEW
    nop

v_dualoff:                        # hook 0x001623B0 (entry of "remove the two-view render tasks")
    lui t7,0x000F
    lw t6,{O_ON}(t7)
    beq t6,zero,v_d_orig          # not ours: the game's own behaviour
    lui t5,%hi(SPR_B_X)
    sw zero,{O_ON}(t7)
    sw zero,{O_CAM2T}(t7)         # player 2's camera has no target while it is not shown
    sh zero,%lo(SPR_B_X)(t5)      # view picture B back to x = 0 for the game's own cross-fades
    lui t4,%hi(DUAL_FLAG)
    lbu t3,%lo(DUAL_FLAG)(t4)
    beq t3,zero,v_d_orig          # the caller has already put the one-view tasks back (event end)
    nop
    addiu sp,sp,-16               # ours is taken down with no one-view tasks installed: remove, then install them
    sd ra,0(sp)
    jal TASKS_OF
    nop
    lw a0,4(v0)
    li a1,5
    jal TASK_REMOVE_GROUP
    li a2,5
    jal SINGLE_ON
    nop
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
v_d_orig:
    addiu sp,sp,-16               # the two instructions that sat at 0x001623B0
    j DUAL_OFF_BODY
    sd ra,0(sp)

v_fade0:                          # hook 0x00161E38 (was: jal 0x001619E8): the game starts its own two-view cross-fade
    lui t7,0x000F
    lw t6,{O_ON}(t7)
    beq t6,zero,v_f_plain
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal DUAL_OFF                  # ours is on: take it down first (this puts the one-view tasks back)
    nop
    ld ra,0(sp)
    addiu sp,sp,16
v_f_plain:
    j SINGLE_OFF                  # then what the game wanted: remove the one-view tasks (it installs two views next)
    nop

v_compose:                        # hook 0x00161C7C (was: j 0x00161AA8): the two-view "put on screen" task
    lui t7,0x000F
    lw t6,{O_ON}(t7)
    bne t6,zero,v_k_ours
    nop
    j COMPOSE                     # the game's own cross-fade: blended, full size, as before
    nop
v_k_ours:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    lui s0,%hi(SPR_A)
    addiu s0,s0,%lo(SPR_A)
    lui s1,%hi(SPR_B)
    addiu s1,s1,%lo(SPR_B)
    lui t7,0x004F                 # one-time set-up of the two sprites, as in the game's routine
    lb t6,0x3B50(t7)
    bne t6,zero,v_k_i1
    nop
    jal SPR_INIT
    move a0,s0
    lui t7,0x004F
    li t6,1
    sb t6,0x3B50(t7)
    lui a0,0x0016
    jal ATEXIT
    addiu a0,a0,0x23D8
v_k_i1:
    lui t7,0x004F
    lb t6,0x3B58(t7)
    bne t6,zero,v_k_i2
    nop
    jal SPR_INIT
    move a0,s1
    lui t7,0x004F
    li t6,1
    sb t6,0x3B58(t7)
    lui a0,0x0016
    jal ATEXIT
    addiu a0,a0,0x23F0
v_k_i2:
    move a0,s0                    # picture A = view 1 = PLAYER 2
    jal SPR_SETA
    li a1,0x156
    move a0,s0
    jal SPR_SETB
    move a1,zero
    li t6,{AX}
    sh t6,8(s0)
    li t6,{AY}
    sh t6,10(s0)
    move a0,s0
    li a1,{W}
    jal SPR_SIZE
    li a2,{H}
    lui a2,0x1A08
    lui a1,0x0008
    move a0,s0
    ori a2,a2,0x2008
    jal SPR_UV                    # the whole 512 x 416 view picture
    ori a1,a1,0x0008
    lui t7,0x0037
    move a0,s0
    jal SPR_TEX
    ld a1,-19336(t7)              # 0x0036B478: where view picture A lives
    li a3,128
    li t0,128                     # full weight (no blending)
    li a2,128
    li a1,128
    jal SPR_COLOR
    move a0,s0
    jal SPR_DRAW
    move a0,s0
    jal SPR_MID
    li a0,0x140
    move a0,s1                    # picture B = view 0 = PLAYER 1
    jal SPR_SETA
    li a1,0x156
    move a0,s1
    jal SPR_SETB
    move a1,zero
    li t6,{BX}
    sh t6,8(s1)
    li t6,{BY}
    sh t6,10(s1)
    move a0,s1
    li a1,{W}
    jal SPR_SIZE
    li a2,{H}
    lui a2,0x1A08
    lui a1,0x0008
    move a0,s1
    ori a2,a2,0x2008
    jal SPR_UV
    ori a1,a1,0x0008
    lui t7,0x0037
    move a0,s1
    jal SPR_TEX
    ld a1,-19328(t7)              # 0x0036B480: where view picture B lives
    li a3,128
    li t0,128
    li a2,128
    li a1,128
    jal SPR_COLOR
    move a0,s1
    jal SPR_DRAW
    move a0,s1
    lui t7,0x000F
    li t6,1
    sb t6,{O_PENDING}(t7)         # the picture of this step is a two-view picture
    jal SET_VIEW                  # everything drawn after this (HUD, marks) starts from view 0
    move a0,zero
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32

v_send:                           # hook 0x0014CFC0 (was: j 0x0014E5F0): the step's draw list goes to the graphics chip
    lui t7,0x000F
    lbu t6,{O_PENDING}(t7)
    sb t6,{O_SHOWN}(t7)           # THE CONTRACT BYTE: layout of the picture that is sent now
    j SEND
    sb zero,{O_PENDING}(t7)
"""

PAD_SITES = [0x001403D4, 0x00140778, 0x0014E940, 0x001585F8, 0x00158DDC, 0x001590E8, 0x001594A0, 0x0015A5E4]


def build(opts):
    without = {"base"}
    if "noexits" in opts:
        without.add("exits")        # TEST ONLY: player 1 alone can trigger exits and events
    sections, hooks = make_all.build(without, True)
    if "noviews" in opts:
        return sections, hooks, {}
    sym = dict(make_all.SYM)
    sym.update(VSYM)
    stack = "stack" in opts
    fmt = dict(O)
    fmt.update(hold_branch="nop" if "nohold" in opts else "bne t3,zero,v_c_no",
               pad_index="move a0,zero" if "nostick" in opts else "sltu a0,zero,t1",
               AX=0, AY=0, BX=0 if stack else 256, BY=208 if stack else 0,
               W=512 if stack else 256, H=208 if stack else 416)
    src = VIEWS_SRC.format(**fmt)
    rows, syms = make_all.asm_lines(VIEWS_AT, src, sym)
    assert rows[-1][0] + 4 <= VIEWS_END, "views section too long"
    sections.append(("views", "lane V1 two views: a camera and a view picture for each hero; one view when it makes no sense", rows))
    jal, jmp = make_all.jal, make_all.jmp
    add = [
        (0x00140CC8, jmp(syms["v_camtask"]), 0x27BDFFF0, "camera task: camera 1, camera 2, and the decision one view / two views"),
        (0x00140CCC, 0, 0x3C040035, "delay slot of the jump (was lui a0,0x35)"),
        (0x00161C7C, jmp(syms["v_compose"]), jmp(0x00161AA8), "two-view 'put on screen' task: ours = side by side at full weight"),
        (0x0014CFC0, jmp(syms["v_send"]), jmp(0x0014E5F0), "end of step: publish the layout byte when the picture is sent"),
        (0x001623B0, jmp(syms["v_dualoff"]), 0x27BDFFF0, "remove two-view tasks: if they were ours, clean up and put one view back"),
        (0x001623B4, 0, 0xFFBF0000, "delay slot (was sd ra,0(sp); moved into v_dualoff)"),
        (0x00161E38, jal(syms["v_fade0"]), jal(0x001619E8), "the game's own two-view cross-fade starts: take ours down first"),
    ]
    for site in PAD_SITES:
        add.append((site, jal(syms["v_pad"]), jal(0x00167F18), "camera code reads the controller: controller 2 for player 2's camera"))
    if "nolock" not in opts:
        add += [
            (0x0019CC58, jal(syms["v_w_unlock"]), jal(0x0019D480), "lock-on manager lets go: player 2's acts on player 2's camera"),
            (0x0019CB00, jal(syms["v_w_lock"]), jal(0x0019D438), "lock-on manager locks on: player 2's acts on player 2's camera"),
            (0x0019CA04, jal(syms["v_w_att"]), jal(0x0015A638), "lock-on manager attached while locked: same rule"),
            (0x0019D09C, jal(syms["v_w_tgt"]), jal(0x0015A6C8), "lock-on manager hands its target to the camera: same rule"),
        ]
    if "nomove" not in opts:
        add.append((0x0017837C, jal(syms["v_view"]), jal(0x00106A60), "stick -> direction: the twin's stick is turned by camera 2's view"))
    for a, w, orig, meaning in add:
        hooks.append((a, w, orig, "views", meaning))
    return sections, hooks, syms


def main():
    args = [a for a in sys.argv[1:]]
    out = ROOT / "patches" / "lane-v1-two-views"
    if args and (":" in args[0] or "/" in args[0] or chr(92) in args[0]):
        out = pathlib.Path(args.pop(0))
    opts = set(args)
    sections, hooks, syms = build(opts)
    word = make_all.load_elf_words()
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
    names = [n for n, _, _ in sections]
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project, lane V1: merged build v2 + two views (" + " + ".join(names) + "); options: " + (" ".join(sorted(opts)) or "none") + ".",
             "comment=Every PC in an online game must have this same file (it changes game code)."]
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hook_words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hook_words[a]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    lst = ["Lane V1 patch (merged v2 + two views) for CRC F266B00B. Every word the patch file writes, with its meaning.",
           "Options: " + (" ".join(sorted(opts)) or "none"), ""]
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
    lst.append("LANE V1 DATA (not written by the patch file; relies on that memory being zero at boot)")
    for k in ("V_CG2", "V_CAM2", "V_SHOWN", "V_PENDING", "V_ON", "V_REQ", "V_DEPTH"):
        lst.append("  %08X  %s" % (VSYM[k], k))
    (out / "listing.txt").write_text("\n".join(lst) + "\n")
    nv = sum(len(r) for n, _, r in sections if n == "views")
    print("%d code words (%d in views), %d hook words -> %s" % (len(code), nv, len(hook_words), out / "SLPM-66675_F266B00B.pnach"))
    if nv:
        rows = [r for n, _, r in sections if n == "views"][0]
        print("   views 0x%08X-0x%08X" % (rows[0][0], rows[-1][0] + 3))


if __name__ == "__main__":
    main()
