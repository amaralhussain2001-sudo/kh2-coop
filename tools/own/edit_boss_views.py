"""One-off: own screens, BOSS MOVES KEEP TWO VIEWS.
  - tools/own/fork_views.py: three changes to lane V1's camera task (the fork is made again by running it);
  - tools/own/make_own.py: step 8, the routines at 0x000F5C00 (option --no-bossviews leaves the whole change out).
What was there: while an event holds the camera (0x0033CC38) both screens show one view. A boss's scripted move
(Twilight Thorn's Reaction Commands) is such an event, the other hero can still walk during it (test
z2-thorn-walk), but his player saw the move's picture instead of his own.
Found (test z4-thorn-ev): the event object (0x0035037C) of a scripted move names the hero in it at +0x44; a story
scene has 0 there.
New rule: a story scene (or a hold without an event) -> one view, as before. A scripted move with a hero in it ->
two views stay. Player 1's hero in the move: his screen shows the move (the game's own), camera 2 goes on for
the twin (its update runs with the hold lifted). The twin in the move: the move's picture (view 0's data) is
copied to view 1 = player 2's screen, and camera 1 goes on for player 1's hero.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# ---------- fork_views.py ----------
p = HERE / "fork_views.py"
t = p.read_text(encoding="utf-8")
if "BM_HOLD" not in t:
    add = r'''
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
'''
    marker = "# 0b. FIX (2026-11-10, tests u3-roundtrip"
    assert t.count(marker) == 1
    t = t.replace(marker, add.lstrip("\n") + "\n" + marker)
    p.write_text(t, encoding="utf-8")
    print("fork_views.py changed")

# ---------- make_own.py ----------
q = HERE / "make_own.py"
s = q.read_text(encoding="utf-8")
if "BOSSV_SRC" not in s:
    block = r'''BOSSV_AT = 0x000F5C00             # step 8: boss moves keep two views (0x000F5C00-0x000F5DFF; variable 0x000F5DF0)
BOSSV_END = 0x000F5DF0
BOSSV_SRC = """
    j bm_hold                     # 0x000F5C00
    nop
    j bm_cam1                     # 0x000F5C08
    nop
    j bm_cam2                     # 0x000F5C10
    nop
bm_hold:                          # v0 = 1 when one view is wanted
    lui t7,0x000F
    lw t8,0x05CC(t7)              # the twin
    beq t8,zero,bh_yes            # no twin in this room
    lui t2,0x0034
    lw t3,-13256(t2)              # 0x0033CC38: an event holds the camera
    beq t3,zero,bh_no
    lui t4,0x0035
    lw t5,0x037C(t4)              # 0x0035037C: the event object
    beq t5,zero,bh_yes
    nop
    lw t6,0x44(t5)                # the hero a scripted move holds (a story scene: 0)
    beq t6,t8,bh_no
    lw t9,-5816(t4)               # player 1's hero
    beq t6,t9,bh_no
    nop
bh_yes:
    jr ra
    li v0,1
bh_no:
    jr ra
    move v0,zero
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
    lw t8,0x05CC(t7)
    beq t8,zero,b1_plain
    lui t2,0x0034
    lw t3,-13256(t2)
    beq t3,zero,b1_plain
    lui t4,0x0035
    lw t5,0x037C(t4)
    beq t5,zero,b1_plain
    nop
    lw t6,0x44(t5)
    bne t6,t8,b1_plain            # the twin is not the hero of this move: camera 1 as the game does it
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
    sw t0,0x5DF0(t7)              # camera 2 leaves view 1 alone in this step
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
    lw t0,0x5DF0(t7)
    beq t0,zero,b2_go
    lui t2,0x0034
    jr ra                         # the move's picture is in view 1 already
    sw zero,0x5DF0(t7)
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


def add_boss_views(result, origin):
    """Step 8: the routines the camera task of tools/own/views.py calls (BM_HOLD, BM_CAM1, BM_CAM2)."""
    code, _labels = assemble(BOSSV_AT, BOSSV_SRC, {})
    code = [w if isinstance(w, int) else w[1] for w in code]
    assert BOSSV_AT + 4 * len(code) <= BOSSV_END, "boss views: too long (%d words)" % len(code)
    for i, w in enumerate(code):
        a = BOSSV_AT + 4 * i
        assert a not in result, "boss views: address already used %08X" % a
        result[a] = w
        origin[a] = "own screens step 8 (a boss's scripted move keeps two views)"
    return len(code)


def add_menu_rows('''
    old = "def add_menu_rows("
    assert s.count(old) == 1
    s = s.replace(old, block)
    old = '''    out.mkdir(parents=True, exist_ok=True)
    head = ['''
    assert s.count(old) == 1
    s = s.replace(old, '''    # 8. A BOSS'S SCRIPTED MOVE KEEPS TWO VIEWS (tools/own/edit_boss_views.py has the story). The camera task of
    # tools/own/views.py calls three routines here unless the fork was made with --no-bossviews.
    if "--no-bossviews" not in sys.argv and park:
        add_boss_views(result, origin)

    out.mkdir(parents=True, exist_ok=True)
    head = [''')
    q.write_text(s, encoding="utf-8")
    print("make_own.py changed")
