"""Lane K (own-screen study) DEMO patch generator. CRC F266B00B, KH2 Final Mix SLPM-66675. NOT production code.

  python -I tools/lane-k/make_k.py <outDir> [options...]

Base: lane E's identity + exit rule (its generator is copied into this folder), so player 1's hero is the engine's
player on controller 1 and the twin (pointer at 0x000F05CC) is on controller 2.

Options:
  dual     keep a second camera for the twin and switch the engine into its own TWO-VIEW render mode
           (the mode the game uses for camera cross-fades: the scene is drawn twice per step, once per view)
  sbs      show the two views side by side (left half / right half) instead of blended on top of each other
  stack    show the two views one above the other (top half / bottom half)
  alpha=A,B  blend weights of the two view pictures (0..128 each; default 128,128)
  nocam2   'dual' without the second camera (both views use the game's camera): control experiment
  nostick  do not give camera 2 its own right stick (it then listens to controller 1)
  move     the twin's left stick is turned by camera 2's view (movement relative to its own camera)

Code cave: 0x000F0E00-0x000F0F07 routines, 0x000F0F08 flag byte, 0x000F0F10-0x000F0FFF second camera block.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from asm import assemble  # noqa: E402
import make_e  # noqa: E402
import e_exit  # noqa: E402

SYM = dict(make_e.SYM)
SYM.update({
    "CAM1": 0x00348710,           # the game's camera object (0xF0 bytes; target object at +0x44, mode at +0x40)
    "CAM_UPDATE": 0x00140B68,     # game: camera update (camera, flag)
    "CAM_INIT": 0x0013F558,       # game: camera reset from its target
    "SET_VIEW": 0x001069F8,       # game: choose the current view index (0 or 1)
    "DUAL_FLAG": 0x0033CC44,      # game: 1 while the two-view render tasks are installed
    "SINGLE_OFF": 0x001619E8,     # game: remove the one-view render tasks
    "DUAL_ON": 0x001620A8,        # game: install the two-view render tasks
    "VIEW_INDEX": 0x0033CC40,     # game: current view index
    "STICK_TO_DIR": 0x00178330,   # game: stick -> world direction, through the current view
    "GET_VIEW": 0x00106A60,       # game: view block getter
    "K_BASE": 0x000F0000,
})

K_CODE = """
k_camtask:                         # replaces the body of the camera task 0x00140CC8
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui a0,%hi(CAM1)
    addiu a0,a0,%lo(CAM1)
    jal CAM_UPDATE                 # camera 1 as the game does it (writes view 0)
    move a1,zero
    lui s0,0x000F
    lw t0,0x05CC(s0)               # twin object (lane E's variable), 0 if none
    beq t0,zero,k_done
    lui t1,%hi(DUAL_FLAG)
    lbu t2,%lo(DUAL_FLAG)(t1)
    bne t2,zero,k_have
    nop
    jal SINGLE_OFF                 # remove the one-view draw tasks
    nop
    jal DUAL_ON                    # install the game's two-view draw tasks
    nop
    lui t3,%hi(CAM1)
    addiu t3,t3,%lo(CAM1)
    addiu t4,s0,0x0F10
    addiu t5,t3,0xF0
k_copy:                            # camera 2 starts as a copy of camera 1
    lw t6,0(t3)
    addiu t3,t3,4
    sw t6,0(t4)
    bne t3,t5,k_copy
    addiu t4,t4,4
    lw t0,0x05CC(s0)
    sw t0,0x0F54(s0)               # camera 2 target = twin
    jal CAM_INIT
    addiu a0,s0,0x0F10
k_have:
    {skip_cam2}
    lw t0,0x05CC(s0)
    sw t0,0x0F54(s0)
    jal SET_VIEW                   # view index 1 while camera 2 updates (k_pad reads it as the controller index)
    li a0,1
    addiu a0,s0,0x0F10
    jal CAM_UPDATE                 # camera 2 (writes view 1)
    move a1,zero
    jal SET_VIEW                   # back to view index 0
    move a0,zero
k_done:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
k_pad:                             # hook 0x001403D4: the follow camera's controller = current view index (0 or 1)
    lui t0,%hi(VIEW_INDEX)
    j GET_PAD
    lw a0,%lo(VIEW_INDEX)(t0)
k_mvB:                             # hook 0x001785F4: stick -> direction, caller holds the player object in s1
    b k_mvX
    move t4,s1
k_mvA:                             # hook 0x001784E8: same, caller holds the player object in s0
    move t4,s0
k_mvX:
    lui t1,0x000F
    lw t2,0x05CC(t1)
    xor t3,t4,t2
    sltiu t3,t3,1                  # 1 if the moving hero is the twin
    j STICK_TO_DIR                 # continue into the game's routine (it returns to the original caller)
    sb t3,0x0F08(t1)
k_view:                            # hook 0x0017837C inside that routine: which view's matrix turns the stick
    lui t1,0x000F
    lbu t2,0x0F08(t1)
    beq t2,zero,k_v0
    sb zero,0x0F08(t1)
    lui v0,0x003A
    jr ra
    ori v0,v0,0x8000               # view 1 block 0x003A8000 (camera 2)
k_v0:
    j GET_VIEW
    li a0,1
"""


def build(opts):
    code, hooks, notes = make_e.build(set())
    e_exit.add(code, hooks, notes, make_e.SYM, {"exit"})
    extra = []                                   # raw pnach lines (memory writes repeated every video frame)
    if "dual" in opts:
        src = K_CODE.format(skip_cam2="b k_done" + chr(10) + "    nop" if "nocam2" in opts else "")
        if "move" not in opts:                       # without the movement hooks leave their routines out
            src = src[:src.index("k_mvB:")]
        words, syms = assemble(0x000F0E00, src, SYM)
        assert 0x000F0E00 + 4 * len(words) <= 0x000F0F08, "routine too long: %d words" % len(words)
        for i, w in enumerate(words):
            code[0x000F0E00 + 4 * i] = w
        hooks[0x00140CC8] = make_e.j(syms["k_camtask"])      # was: addiu sp,sp,-16
        hooks[0x00140CCC] = 0                                # was: lui a0,0x35 (delay slot of the jump now)
        if "nostick" not in opts:
            hooks[0x001403D4] = make_e.jal(syms["k_pad"])    # was: jal 0x00167F18 (follow camera, index 0)
        if "move" in opts:
            hooks[0x001784E8] = make_e.jal(syms["k_mvA"])    # was: jal 0x00178330
            hooks[0x001785F4] = make_e.jal(syms["k_mvB"])    # was: jal 0x00178330
            hooks[0x0017837C] = make_e.jal(syms["k_view"])   # was: jal 0x00106A60
            notes.append("twin's stick is turned by camera 2's view")
        notes.append("lane K demo: second camera + two-view render mode, routines 0x000F0E00-0x%08X"
                     % (0x000F0E00 + 4 * len(words) - 1))
        a, b = 128, 128
        for o in opts:
            if o.startswith("alpha="):
                a, b = [int(x) for x in o[6:].split(",")]
        extra.append("patch=1,EE,0034C76C,extended,%08X" % a)   # blend weight of view picture A (byte)
        extra.append("patch=1,EE,0034C768,extended,%08X" % b)   # blend weight of view picture B (byte)
        if "sbs" in opts:
            hooks[0x00161B38] = 0x24050100                   # picture A: width 512 -> 256
            hooks[0x00161BB4] = 0x24050100                   # picture B: width 512 -> 256
            extra.append("patch=1,EE,104F3E78,extended,00000100")   # picture B: x = 256 (16-bit write)
            notes.append("views side by side")
        if "stack" in opts:
            hooks[0x00161B40] = 0x240600D0                   # picture A: height 416 -> 208
            hooks[0x00161BBC] = 0x240600D0                   # picture B: height 416 -> 208
            extra.append("patch=1,EE,104F3E7A,extended,000000D0")   # picture B: y = 208 (16-bit write)
            notes.append("views one above the other")
    return code, hooks, notes, extra


def main():
    out = pathlib.Path(sys.argv[1])
    opts = set(sys.argv[2:])
    code, hooks, notes, extra = build(opts)
    out.mkdir(parents=True, exist_ok=True)
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project, lane K DEMO (study, not for play): " + "; ".join(notes) + ".",
             "comment=Every PC in a linked test must have this same file (it changes game code)."]
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hooks):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hooks[a]))
    lines += extra
    (out / "SLPM-66675_F266B00B.pnach").write_text(chr(10).join(lines) + chr(10))
    print("%d code words, %d hook words, %d repeated writes -> %s" % (len(code), len(hooks), len(extra), out / "SLPM-66675_F266B00B.pnach"))
    for n in notes:
        print("  ", n)


if __name__ == "__main__":
    main()
