"""One-off: tools/own/make_own.py, the option --cannon2view (ninth round, job 5), fourth form.
MEASURED with tools/own/cam_probe.py (run cnD): in the toy cannon game the game's camera is NOT the cannon camera
(kind 10); it is kind 0 with a still eye (0, -316, 804) and aim point (0, -239, 416), target = player 1's cannon,
while both cannon objects turn with their sticks. So the forms before (camera 2 forced to kind 10) gave player
2 a view that swung with a cannon. They are taken out again (the call at 0x00140C9C is the game's own again).
Now, while the twin is a toy cannon: camera 2 is not worked out at all. Each step it becomes a copy of camera
1 as the game left it (camera 1 sits in player 2's store 0x000F6E00 while camera 2 is in the game's camera
memory), with the twin as its target and its six places (camera + 0x00 aim, + 0x10 eye, + 0x60 / + 0x70 wished
eye, + 0x80 / + 0x90 wished aim) moved by the way from player 1's cannon to the twin's; then the game's own
"write the view" 0x001408A0 runs for it. So player 2 has the game's still view, centred behind HIS cannon.
Without the option the builder writes what it wrote before, bit for bit.
The record of the edit; run once:
  python -I tools/own/edit_make_own_cannon5.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "make_own.py"
s = p.read_text(encoding="utf-8")
if "cn_view:" in s:
    raise SystemExit("already there")

# (1) step 8's piece and the hook
a = s.index('    if "--cannon2view" in sys.argv:                 # (ninth round, job 5) the toy cannon: a view for each player' + NL)
end_mark = '        origin[a] = "own screens step 8 hook: the toy cannon\'s camera looks along the cannon of the camera\'s own hero"' + NL
b = s.index(end_mark, a) + len(end_mark)
new = '''    syms8 = {}
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
'''
s = s[:a] + new + s[b:]

# (2) the block's source
a = s.index("CN_AT = 0x000F7400")
b = s.index('"""' + NL, s.index('CN_SRC = """', a) + 12) + len('"""' + NL)
new = '''CN_AT = 0x000F7400                # (--cannon2view) the toy cannon's view for each player: 0x000F7400-0x000F74FF
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
'''
s = s[:a] + new + s[b:]
with open(p, "w", encoding="utf-8", newline=chr(13) + chr(10)) as f:      # the file has CRLF line ends
    f.write(s)
print("ok")
