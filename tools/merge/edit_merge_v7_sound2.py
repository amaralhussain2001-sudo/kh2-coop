r"""One-off (STATE part 148; the user's words 2026-11-18: "is there a way to fix the sounds?" then "okay go aheed with your suggestion"
= option 2: every 3D sound is heard from the NEARER of the two cameras): THE EIGHTY-FIFTH GLUE, option --sound2.
Research (local\analysis\sound\notes.txt): the game's 3D sound routine 0x002BB5F8 (a0 = a sound of the list 0x01E2AA80: +0 its
position) takes the view block of the view getter 0x00106A60(0) - view 0, camera 1 = player 1's - turns the position into that
camera's space (block +16, a 4x4 matrix), and from it writes the volume (+40, 16383 - distance^2 / k) and the pan (+44). An AREA
sound (kind +49 = 4, a river, a waterfall) first gets its position from 0x0014EE28: the point of the area nearest to the camera's
eye (view block +0x50, also from 0x00106A60(0)). With two views (the own-screen build: V_ON 0x000F6F04, camera 2 writes view 1's
block 0x003A8000 = view 0's 0x003A7F70 + 0x90) player 2's fights were heard from player 1's camera only.
Now:
  sn_view (0x002BB630, was jal 0x00106A60): the game's answer; with two views, a twin and that answer = view 0's block: the
          squared distance of the sound to camera 1's eye and to camera 2's eye; camera 2 nearer -> view 1's block. So volume and
          pan come from the same camera (the nearer one). Same on both PCs (only game data is used).
  sn_area (0x002BB968, was jal 0x0014EE28): with two views and a twin: the area's point once for camera 2 (V_SNFORCE = 1 makes
          sn_get answer view 1's block) into a spare place, then as the game for camera 1 into the sound; the point nearer to its
          own camera's eye is kept (with its "inside" byte). Then sn_view picks that camera.
  sn_get (0x0014EE64, was jal 0x00106A60, inside 0x0014EE28 only): view 1's block while V_SNFORCE (0x000DE830) is 1, else the game.
One view (shared-screen build, story scenes, no twin): everything as the game. Without --sound2 the builder writes exactly what it
wrote before.
  python -I tools/merge/edit_merge_v7_sound2.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--sound2" in t:
    raise SystemExit("already done")

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTY-FIFTH GLUE (built only with the option --sound2): EVERY 3D SOUND IS HEARD FROM THE NEARER CAMERA. The game's 3D sound
routine 0x002BB5F8 took camera 1 (view 0) for every sound. sn_view (0x002BB630): with two views (V_ON) and a twin, the camera whose
eye (view block +0x50) is nearer to the sound gives its view block (view 1 = 0x003A8000), so volume and pan come from it. sn_area
(0x002BB968): an area sound's point is taken for both cameras (sn_get 0x0014EE64 answers view 1 while V_SNFORCE 0x000DE830 is 1)
and the one nearer to its camera is kept. Room 0x000DE900 .. 0x000DEB80.
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eighty-fifth glue (only with --sound2) ----------------------------------------------------------------------
SN_AT = 0x000DE900
SN_END = 0x000DEB80
SN_HOOKS = ((0x002BB630, 0x0C041A98, "sn_view"), (0x002BB968, 0x0C053B8A, "sn_area"), (0x0014EE64, 0x0C041A98, "sn_get"))
SN_SRC = """
sn_view:                          # 0x002BB630 (was jal 0x00106A60, a0 = 0) in the 3D sound routine; s1 = the sound (+0 position)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00106A60                # the game's view block
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    lui t7,0x000F
    lw t6,0x6F04(t7)              # V_ON: two views (camera 2 writes view 1)
    beq t6,zero,sv_out
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,sv_out
    lui t5,0x003A
    ori t5,t5,0x7F70              # view 0's block
    bne v0,t5,sv_out              # the game took another block just now: as it is
    nop
    lwc1 f2,0(s1)                 # the sound's position
    lwc1 f3,4(s1)
    lwc1 f4,8(s1)
    lwc1 f5,0x50(t5)              # camera 1's eye
    lwc1 f6,0x54(t5)
    lwc1 f7,0x58(t5)
    sub.s f5,f5,f2
    sub.s f6,f6,f3
    sub.s f7,f7,f4
    mul.s f5,f5,f5
    mul.s f6,f6,f6
    mul.s f7,f7,f7
    add.s f5,f5,f6
    add.s f5,f5,f7                # to camera 1, squared
    lwc1 f8,0xE0(t5)              # camera 2's eye (view 1's block + 0x50)
    lwc1 f9,0xE4(t5)
    lwc1 f10,0xE8(t5)
    sub.s f8,f8,f2
    sub.s f9,f9,f3
    sub.s f10,f10,f4
    mul.s f8,f8,f8
    mul.s f9,f9,f9
    mul.s f10,f10,f10
    add.s f8,f8,f9
    add.s f8,f8,f10               # to camera 2, squared
    c.lt.s f8,f5
    bc1f sv_out                   # camera 1 nearer (or as near): as the game
    nop
    addiu v0,t5,0x90              # view 1's block: heard from camera 2
sv_out:
    jr ra
    nop
sn_get:                           # 0x0014EE64 (was jal 0x00106A60) inside the area routine 0x0014EE28
    lui t7,0x000E
    lw t6,-6096(t7)               # V_SNFORCE (0x000DE830)
    beq t6,zero,sg_game
    lui v0,0x003A
    jr ra
    ori v0,v0,0x8000              # view 1's block (camera 2's eye)
sg_game:
    j 0x00106A60
    nop
sn_area:                          # 0x002BB968 (was jal 0x0014EE28): a0 = the area, a1 = the sound, a2 = its "inside" byte
    lui t7,0x000F
    lw t6,0x6F04(t7)
    beq t6,zero,sa_game
    lw t6,0x05CC(t7)
    beq t6,zero,sa_game
    nop
    addiu sp,sp,-80
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s0,a0
    move s1,a1
    move s2,a2
    lui t7,0x000E
    addiu t6,zero,1
    sw t6,-6096(t7)               # V_SNFORCE = 1: camera 2
    addiu a1,sp,48                # its point (16 bytes, aligned)
    jal 0x0014EE28
    addiu a2,sp,40                # its "inside" byte
    move s3,v0
    lui t7,0x000E
    sw zero,-6096(t7)             # V_SNFORCE = 0
    move a0,s0
    move a1,s1
    jal 0x0014EE28                # camera 1, as the game, into the sound
    move a2,s2
    beq s3,zero,sa_done           # no point for camera 2: camera 1's answer
    nop
    beq v0,zero,sa_two            # no point for camera 1: camera 2's
    nop
    lui t5,0x003A
    ori t5,t5,0x7F70
    lwc1 f2,0(s1)                 # camera 1's point to camera 1's eye, squared
    lwc1 f3,4(s1)
    lwc1 f4,8(s1)
    lwc1 f5,0x50(t5)
    lwc1 f6,0x54(t5)
    lwc1 f7,0x58(t5)
    sub.s f5,f5,f2
    sub.s f6,f6,f3
    sub.s f7,f7,f4
    mul.s f5,f5,f5
    mul.s f6,f6,f6
    mul.s f7,f7,f7
    add.s f5,f5,f6
    add.s f5,f5,f7
    lwc1 f2,48(sp)                # camera 2's point to camera 2's eye, squared
    lwc1 f3,52(sp)
    lwc1 f4,56(sp)
    lwc1 f8,0xE0(t5)
    lwc1 f9,0xE4(t5)
    lwc1 f10,0xE8(t5)
    sub.s f8,f8,f2
    sub.s f9,f9,f3
    sub.s f10,f10,f4
    mul.s f8,f8,f8
    mul.s f9,f9,f9
    mul.s f10,f10,f10
    add.s f8,f8,f9
    add.s f8,f8,f10
    c.lt.s f8,f5
    bc1f sa_done                  # camera 1's point is as near or nearer: kept
    nop
sa_two:
    lw t0,48(sp)                  # camera 2's point into the sound
    lw t1,52(sp)
    lw t2,56(sp)
    lw t3,60(sp)
    sw t0,0(s1)
    sw t1,4(s1)
    sw t2,8(s1)
    sw t3,12(s1)
    lbu t0,40(sp)
    sb t0,0(s2)                   # and its "inside" byte
    addiu v0,zero,1
sa_done:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,80
sa_game:
    j 0x0014EE28
    nop
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--sound2" in sys.argv:                                             # eighty-fifth glue (3D sound from the nearer camera)
        code, labels = assemble(SN_AT, SN_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert SN_AT + 4 * len(code) <= SN_END, "the eighty-fifth glue does not fit"
        clash = [a for a in words if SN_AT <= a < SN_END or 0x000DE830 <= a < 0x000DE834]
        assert not clash, "patch words in the eighty-fifth glue's room: %08X" % clash[0]
        for i, w in enumerate(code):
            a = SN_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (3D sound from the nearer camera)"
        for a, w0, label in SN_HOOKS:
            hook_game(a, w0, jal(labels[label]), "3D sound from the nearer camera: " + label)
        n_glue += len(code) + 3

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-fifth glue (--sound2) added")
