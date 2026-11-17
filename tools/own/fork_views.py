"""Make tools/own/views.py: lane V1's generator (tools/lane-v1/make_v1.py, read only) with the KEEP change (the
default, used by the own-screen build) and the PARK experiments.

  python -I tools/own/fork_views.py

WHY. In lane V1's delivered patch player 1's finished 3D picture leaves the graphics chip: the game's own capture
reads it back to main memory at the end of the first pass and loads it again for the 2D part. With a raised
picture quality in the emulator that round trip brings it back at the PS2's own resolution, so player 1's 3D is
less sharp than player 2's (lane V3 measured 0.81 at 4x; blocky to the eye, test o25-4x).

KEEP (default mode of views.py; VERIFIED 2026-11-10, tests o26-keep-1x / -4x, o30-o32). The game flow stays lane
V1's, word for word. Two LABEL register writes are added: 0x56310003 just before the capture (task at priority
90000, after player 1's HUD was drawn) and 0x56310004 right after the loader (task at 90130). The own-view emulator
(build view12) keeps a copy of the draw buffer at its own resolution at the first and puts it into the frame
buffer at page 112 at the second (settings KeepSaveId / KeepRestoreId / KeepRestoreBlock in the .view file).
Result: at 4x player 1's picture is as sharp as player 2's; at 1x it differs from the plain arrangement by at most
1 colour step in under 1 % of the pixels. An emulator without the change ignores the two writes.

PARK (EXPERIMENT, options "park" and "late"; NOT USED: the words of the command menu disappear).
The idea was to keep player 1's picture inside the graphics chip:
  1. end of the first pass (two-view task at priority 90000): instead of the capture, a copy INSIDE the graphics
     chip (local -> local image transfer, no drawing state is touched): draw buffer (page 216) -> pages 0-103, the
     display buffer's pages. They are the only free pages during the second pass. Player 1's picture is "parked".
  2. the 2D part of the step begins (task at priority 90130): instead of the loader, a second copy inside the
     chip, pages 0-103 -> pages 112-215 (the 3D passes are over, the depth buffer is free). From here on everything
     is lane V1's delivered arrangement, unchanged: the 2D goes into both pictures, second buffer = page 112, the
     HUD's depth at page 320.
  3. end of the step, as before: display copy of the draw buffer (player 2's finished picture), MARKER 2, display
     copy of page 112 (player 1's finished picture), and new: MARKER 1.
  (A first design kept the picture in the display pages through the 2D part, option "late". There the words of the
  command menu were missing in both pictures; why was not found. Kept as an experiment only.)
While a picture is parked, the display pages do not hold a finished picture. So BOTH PCs must show a copy taken at
their own marker (emulator setting: one marker id per player). In the first step of a two-view period one more
marker (MARKER 0, for every PC) is sent just before the first parking, while the display still holds the last
one-view picture, and the layout byte is set to 2 at once, so no PC ever shows the display pages mid-step.

Markers (LABEL register writes that change nothing): 0x56310000 everybody, 0x56310001 player 1, 0x56310002 player 2.
An emulator without the own-view change shows a wrong picture in this mode; both players need the own-view build.
WHAT WAS FOUND (tests o3-o18, 2026-11-10): with the copy "draw buffer -> display pages" executed, the words of the
command menu (Attack, the ? rows, Save) are missing in BOTH players' pictures, on the hardware AND the software
renderer; with the same packet but TRXDIR = 3 (registers written, no copy) they are there; copying only the top
or only the bottom half removes them too; the second copy (page 0 -> page 112) alone is harmless. So the game
needs the display buffer's memory untouched for those words. Why was not found.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "lane-v1" / "make_v1.py"
DST = HERE / "views.py"

t = SRC.read_text(encoding="utf-8")


def rep(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        raise SystemExit("expected %d place(s), found %d, for: %r" % (count, n, old[:90]))
    t = t.replace(old, new)


# 0. where the file lives now
rep('HERE = pathlib.Path(__file__).resolve().parent\nROOT = HERE.parent.parent\n',
    '# FORK of tools/lane-v1/make_v1.py made by tools/own/fork_views.py (the PARK change). Do not edit by hand:\n'
    '# change fork_views.py and run it again.\n'
    'HERE = pathlib.Path(__file__).resolve().parent\nROOT = HERE.parent.parent\n')

# 0c. BOSS MOVES KEEP TWO VIEWS (tools/own/edit_boss_views.py; routines: tools/own/make_own.py step 8).
import sys as _sys
if "--no-bossviews" not in _sys.argv:
    rep("""    "CAM_HOLD": 0x0033CC38,""", """    "BM_HOLD": 0x000F5C00,        # own-screen step 8: v0 = 1 when one view is wanted (no twin / a story scene)
    "BM_CAM1": 0x000F5C08,        # camera 1's update, also when the twin is the hero of a scripted move
    "BM_CAM2": 0x000F5C10,        # camera 2's update, also while a scripted move holds the camera
    "CAM_HOLD": 0x0033CC38,""")
    rep("""    jal CAM_UPDATE                # camera 1 exactly as the game does it (writes view 0)""",
        """    jal BM_CAM1                   # camera 1 as the game does it (writes view 0); see make_own.py step 8""")
    rep("""    jal CAM_UPDATE                # camera 2 through the game's own update (writes view 1)""",
        """    jal BM_CAM2                   # camera 2 through the game's own update (writes view 1); step 8""")
    rep("""    lw t1,{O_TWIN}(s0)
    beq t1,zero,v_c_no            # no twin in this room
    lui t2,%hi(CAM_HOLD)
    lw t3,%lo(CAM_HOLD)(t2)
    {hold_branch}                 # an event holds the camera: one full view
    nop
""", """    jal BM_HOLD                   # no twin in this room, or a story scene holds the camera: one full view
    nop
    bne v0,zero,v_c_no
    nop
""")

# 0b. FIX (2026-11-10, tests u3-roundtrip, d1-doorstate, d2-doorflag): a room change through a door removes the
# scene's draw tasks, ours included, without going through "remove the two-view tasks". Our flag "two views are on"
# stayed 1 (VERIFIED: 0x000F6F04 = 1 while the game's own flag 0x0033CC44 = 0), so two views were never asked for
# again: after the first door both PCs showed player 1's view. Now the camera task notices it and starts again.
rep("""    lui s0,0x000F
    lw t0,{O_ON}(s0)
    beq t0,zero,v_c_want
    nop
    jal v_enter                   # two views are on: put player 2's camera into the game's camera memory
    nop
""", """    lui s0,0x000F
    lw t0,{O_ON}(s0)
    beq t0,zero,v_c_want
    lui t1,%hi(DUAL_FLAG)
    lbu t1,%lo(DUAL_FLAG)(t1)
    bne t1,zero,v_c_two           # the two-view draw tasks are still installed
    nop
    sw zero,{O_ON}(s0)            # they went away with the scene (a room change through a door): start again
    sw zero,{O_CAM2T}(s0)         # (the same clean-up as v_dualoff)
    lui t5,%hi(SPR_B_X)
    b v_c_want
    sh zero,%lo(SPR_B_X)(t5)
v_c_two:
    jal v_enter                   # two views are on: put player 2's camera into the game's camera memory
    nop
""")

# 1. the 2D part opens: nothing to load, player 1's picture is already in the second buffer
rep("""    jal SPR_MID                   # load player 1's 3D picture into the second buffer (the game's own loader)
    li a0,{BUF2}
{zoff_block}
""", """{load_block}
{zoff_block}
""")

# 2. end of the step
rep("""    jal SEND                      # display registers + copy of the draw buffer to the display = PLAYER 2's finished picture
    move s0,a0
    {p2only}                      # (test builds only: stop here, so the display keeps player 2's picture)
    nop
    lui a0,%hi(pkt_mark)
    jal PKT_SEND                  # THE MARKER: a write to the graphics chip's LABEL register that changes nothing
    addiu a0,a0,%lo(pkt_mark)
    lui t7,%hi(BLIT_TEX0)
    lw t6,%lo(BLIT_TEX0)(t7)
    xori t6,t6,{TX}
    sw t6,%lo(BLIT_TEX0)(t7)      # the display copy now reads the second buffer
    jal PKT_SEND                  # copy to the display again = PLAYER 1's finished picture (what the display keeps)
    move a0,s0
    lui t7,%hi(BLIT_TEX0)
    lw t6,%lo(BLIT_TEX0)(t7)
    xori t6,t6,{TX}
    sw t6,%lo(BLIT_TEX0)(t7)
v_send_end:
""", """    move s0,a0
{unpark_block}
    jal SEND                      # display registers + copy of the draw buffer to the display = PLAYER 2's finished picture
    move a0,s0
    {p2only}                      # (test builds only: stop here, so the display keeps player 2's picture)
    nop
    lui a0,%hi(pkt_mark)
    jal PKT_SEND                  # MARKER 2: a write to the graphics chip's LABEL register that changes nothing
    addiu a0,a0,%lo(pkt_mark)
    lui t7,%hi(BLIT_TEX0)
    lw t6,%lo(BLIT_TEX0)(t7)
    xori t6,t6,{TXS}
    sw t6,%lo(BLIT_TEX0)(t7)      # the display copy now reads player 1's finished picture
    jal PKT_SEND                  # copy to the display again = PLAYER 1's finished picture (what the display keeps)
    move a0,s0
    lui t7,%hi(BLIT_TEX0)
    lw t6,%lo(BLIT_TEX0)(t7)
    xori t6,t6,{TXS}
    sw t6,%lo(BLIT_TEX0)(t7)
{mark1_block}
v_send_end:
""")

# 3. the new routine for the end of the first pass (lane V2's per-view section jumps here instead of the capture)
rep('''ZOFF_BLOCK = """''', '''PARK_SRC = """
v_park:                           # two-view task at priority 90000: the first picture is complete in the draw buffer
    lui t7,0x000F                 # (player 1's 3D picture, and player 1's HUD when lane V2's section is in)
    lw t6,{O_ON}(t7)
    bne t6,zero,v_pk_ours
    nop
    j CAPTURE                     # the game's own cross-fade: its capture to main memory, as before
    nop
v_pk_ours:
    addiu sp,sp,-16
    sd ra,0(sp)
{cap_block}
    lui t7,0x000F
    lbu t6,{O_SHOWN}(t7)
    li t5,2
    beq t6,t5,v_pk_copy           # the picture on the display is already a two-view one: every PC shows a held copy
    nop
    sb t5,{O_SHOWN}(t7)           # first step of a two-view period: the layout byte says "two full pictures" at once ...
    lui a0,%hi(pkt_mark0)
    jal PKT_SEND                  # ... and MARKER 0 lets every PC keep the picture that is on the display now
    addiu a0,a0,%lo(pkt_mark0)
v_pk_copy:
    lui a0,%hi(pkt_park)
    jal PKT_SEND                  # copy inside the graphics chip: draw buffer -> the display pages (player 1's picture parks)
    addiu a0,a0,%lo(pkt_park)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""

KEEP_SRC = """
v_keep:                           # two-view task at priority 90000: the first picture is complete in the draw buffer
    lui t7,0x000F                 # (player 1's 3D picture, and player 1's HUD when lane V2's section is in)
    lw t6,{O_ON}(t7)
    beq t6,zero,v_kp_go           # the game's own cross-fade: only its capture
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    lui a0,%hi(pkt_keep1)
    jal PKT_SEND                  # KEEP marker: an own-view emulator keeps a copy of this picture at its own sharpness
    addiu a0,a0,%lo(pkt_keep1)
    ld ra,0(sp)
    addiu sp,sp,16
v_kp_go:
    j CAPTURE                     # the game's capture to main memory, as in lane V1's arrangement
    nop
"""

KEEP_BLOCK = """    lui a0,%hi(pkt_keep2)
    jal PKT_SEND                  # RESTORE marker: the emulator puts its sharp copy over the picture just loaded
    addiu a0,a0,%lo(pkt_keep2)"""

LOAD_BLOCK = """    jal SPR_MID                   # load player 1's 3D picture into the second buffer (the game's own loader)
    li a0,{BUF2}"""

UNPARK_BLOCK = """    lui a0,%hi(pkt_unpark)
    jal PKT_SEND                  # player 1's picture leaves the display pages: copy inside the chip to page 112
    addiu a0,a0,%lo(pkt_unpark)"""

CAP_BLOCK = """    jal CAPTURE                   # EXPERIMENT ONLY: the game's capture as well
    nop"""

W2D_BLOCK = """    lui a0,%hi(pkt_w2d)
    jal PKT_SEND                  # the 2D part of the step begins: the same depth test setting lane V1's arrangement left
    addiu a0,a0,%lo(pkt_w2d)"""

MARK1_BLOCK = """    lui a0,%hi(pkt_mark1)
    jal PKT_SEND                  # MARKER 1: player 1's finished picture is on the display
    addiu a0,a0,%lo(pkt_mark1)"""

ZOFF_BLOCK = """''')

# 4. constant packets
rep("""def data_src(buf2, zbp):""", """MARK0_ID = 0x56310000             # park mode: every PC keeps the picture that is on the display now
MARK1_ID = 0x56310001             # park mode: player 1's finished picture is on the display
KEEP1_ID = 0x56310003             # keep mode: the frame buffer being drawn to holds player 1's picture: keep a copy
KEEP2_ID = 0x56310004             # keep mode: the picture was loaded into the second buffer: put the copy there


def data_src(buf2, zbp, park=False, keep=False):""")
rep("""    return "\\n".join(out) + "\\n"


def expand(src):""", """    if keep:
        packet("pkt_keep1", [(0x62, KEEP1_ID, 0, "LABEL: ID = 0x%08X, mask = 0" % KEEP1_ID)],
               "KEEP marker: player 1's picture is complete in the draw buffer")
        packet("pkt_keep2", [(0x62, KEEP2_ID, 0, "LABEL: ID = 0x%08X, mask = 0" % KEEP2_ID)],
               "RESTORE marker: the picture was loaded into the second buffer")
    if park:
        def move(name, sbp, dbp, note):
            packet(name, [
                (0x50, 0x00080000 | sbp, 0x00080000 | dbp, "BITBLTBUF: from block 0x%X to block 0x%X, both 512 wide, 32-bit" % (sbp, dbp)),
                (0x51, 0, 0, "TRXPOS: from (0, 0) to (0, 0)"),
                (0x52, 512, 416, "TRXREG: 512 x 416"),
                (0x53, 2, 0, "TRXDIR = 2: copy inside the graphics chip"),
            ], note)
        move("pkt_park", 0xD8 << 5, 0, "player 1's picture: draw buffer (page 216) -> the display pages (page 0)")
        move("pkt_unpark", 0, 0x70 << 5, "player 1's finished picture: page 0 -> the depth pages (page 112)")
        packet("pkt_w2d", [(0x47, 0x00030000, 0, "TEST_1 = always pass")], "the 2D part of the step begins")
        packet("pkt_mark0", [(0x62, MARK0_ID, 0, "LABEL: ID = 0x%08X, mask = 0" % MARK0_ID)],
               "MARKER 0: before the first parking of a two-view period")
        packet("pkt_mark1", [(0x62, MARK1_ID, 0, "LABEL: ID = 0x%08X, mask = 0" % MARK1_ID)],
               "MARKER 1: player 1's finished picture is on the display")
    return "\\n".join(out) + "\\n"


def expand(src):""")

# 4b. the constant packets start a little earlier: the park packets need 0x60 more bytes, and the code got shorter
rep("""DATA_AT = 0x000F6A00              # constant graphics packets""", """DATA_AT = 0x000F69C0              # constant graphics packets""")

# 5. build(): park is the default of this fork ("nopark" gives lane V1's delivered arrangement back)
rep("""    buf2, zbp = (0x140, 0x70) if "tex" in opts else (0x70, 0x140)
    zreloc = zbp != 0x70
    fmt.update(BUF2=buf2, FX=0xD8 ^ buf2, TX=0x1B00 ^ (buf2 << 5), zoff_block=ZOFF_BLOCK if zreloc else "",
               z_cases=Z_CASES.format(**O) if zreloc else "")
    if not sbs:
        drows, dsyms = make_all.asm_lines(DATA_AT, data_src(buf2, zbp), sym)""",
    """    # Modes of this fork:
    #   keep (default)  lane V1's delivered arrangement + two markers for the own-view emulator: it keeps a sharp
    #                   copy of player 1's picture and puts it over the reloaded one. Nothing else changes.
    #   "nopark"        lane V1's delivered arrangement, no markers.
    #   "park"          EXPERIMENT (loses the HUD's words): the picture is parked in the display pages during the
    #                   second pass and goes back to page 112 when the 2D part begins.
    #   "late"          EXPERIMENT (same fault): parked through the 2D part too (second buffer = page 0).
    park = not sbs and ("park" in opts or "late" in opts)
    keep = not sbs and not park and "nopark" not in opts
    late = park and "late" in opts
    buf2, zbp = (0x140, 0x70) if "tex" in opts else (0x70, 0x140)
    if late:
        buf2, zbp = 0x00, 0x70
        if "parkz" in opts:
            zbp = 0x140
    zreloc = zbp != 0x70
    sym["CAPTURE"] = 0x0014E0D8     # the game's capture of the first view picture (what the task at 90000 calls)
    if late:
        load_block = LOAD_BLOCK.format(BUF2=0x70) if "t_load" in opts else ""
    elif park:
        load_block = UNPARK_BLOCK   # instead of the loader: copy inside the graphics chip, page 0 -> page 112
    else:
        load_block = LOAD_BLOCK.format(BUF2=buf2) + ("\\n" + KEEP_BLOCK if keep else "")
    fmt.update(BUF2=buf2, FX=0xD8 ^ buf2, TX=0x1B00 ^ (buf2 << 5),
               zoff_block=ZOFF_BLOCK if zreloc else (W2D_BLOCK if late and "now2d" not in opts else ""),
               z_cases=Z_CASES.format(**O) if zreloc else "",
               TXS=0x1B00 ^ ((0x70 if park else buf2) << 5),
               load_block=load_block,
               cap_block=CAP_BLOCK if "t_capture" in opts else "",
               unpark_block=UNPARK_BLOCK if late else "",
               mark1_block=MARK1_BLOCK if park else "")
    big = park                      # the park packets do not fit behind the code: they go to another free area
    if not sbs:
        drows, dsyms = make_all.asm_lines(0x000F3500 if big else DATA_AT, data_src(buf2, zbp, park, keep), sym)
        assert not big or drows[-1][0] + 4 <= 0x000F3800, "packet data too long for the other area\"""")
rep("""        assert drows[-1][0] + 4 <= VSYM["V_CG2"], "packet data too long\"""",
    """        assert big or drows[-1][0] + 4 <= VSYM["V_CG2"], "packet data too long\"""")
rep("""    assert rows[-1][0] + 4 <= (VIEWS_END if sbs else DATA_AT), "views section too long\"""",
    """    assert rows[-1][0] + 4 <= (VIEWS_END if sbs or big else DATA_AT), "views section too long\"""")
rep("""    src = expand((VIEWS_SRC + (SBS_SRC if sbs else FULL_SRC)).format(**fmt))""",
    """    src = expand((VIEWS_SRC + (SBS_SRC if sbs else FULL_SRC) + (PARK_SRC if park else "")
                  + (KEEP_SRC if keep else "")).format(**fmt))""")

DST.write_text(t, encoding="utf-8")
print("written", DST)
