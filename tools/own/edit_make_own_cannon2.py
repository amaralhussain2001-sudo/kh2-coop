"""One-off: tools/own/make_own.py gets the option --cannon2view (ninth round, job 5: the toy cannon, A VIEW FOR
EACH PLAYER). It takes the place of --cannon1view (never both).
Read (2026-11-15): the toy cannon's camera is the game's camera KIND 10 (the camera object's word + 0x40,
0x00348750). The cannon's builder 0x001CF698 jumps to 0x00158A90: kind = 10 and the global 0x004F35A0 = that cannon.
The camera task's kind 10 step (the call at 0x00140C9C -> 0x001589D0) reads the cannon from that global: its
place and turn (object + 0x40) and the two offsets the cannon's script sets (object + 0xB70 / + 0xB80, the call
"set cannon camera offset") give the eye and the aim point. So with two cannons both cameras looked along the
cannon that was built last, and player 2's own camera (made as a plain follow camera) looked at his cannon from
the front.
What the option does:
  * cn_cam (the call at 0x00140C9C): the cannon that this camera looks along is the hero of the camera that is
    being worked out: the twin while player 2's camera is in the game's camera memory (0x000F6F0C not 0), else
    the engine's player.
  * bm_cam2 (camera 2's step): while the twin is a toy cannon (object 0x03C8) camera 2's kind is 10; when he is
    not one (any more) and the kind is still 10, it is the plain follow camera again.
Without the option the builder writes what it wrote before, bit for bit.
The record of the edit; run once:
  python -I tools/own/edit_make_own_cannon2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "make_own.py"
s = p.read_text(encoding="utf-8")
if "--cannon2view" in s:
    raise SystemExit("already there")
old = "    code, _labels = assemble(BOSSV_AT, src, {})" + NL
new = '''    if "--cannon2view" in sys.argv:                 # (ninth round, job 5) the toy cannon: a view for each player
        assert "--cannon1view" not in sys.argv, "--cannon2view takes the place of --cannon1view"
        x = """bm_cam2:                          # camera 2's update (a0 = the camera, a1 = 0; player 2's camera is swapped in)
    lui t7,0x000F
"""
        assert src.count(x) == 1
        src = src.replace(x, x + """    lw t9,0x05CC(t7)              # the twin
    lui t5,0x0035
    beq t9,zero,b2_k9
    lw t4,-30896(t5)              # camera 2's kind (0x00348750: player 2's camera is in place)
    lw t6,8(t9)
    li t1,10
    lw t6,0(t6)                   # the twin's object number
    xori t6,t6,0x03C8
    beql t6,zero,b2_k9
    sw t1,-30896(t5)              # (only when he is a toy cannon) the cannon's camera kind
    beql t4,t1,b2_k9
    sw zero,-30896(t5)            # (only when he is none and the kind is still the cannon's) the follow camera
b2_k9:
""") + """
cn_cam:                           # the call at 0x00140C9C (camera kind 10 = the toy cannon's): a0 = the camera
    lui t7,0x000F
    lw t0,0x6F0C(t7)              # not 0: player 2's camera is in the game's camera memory
    lui t1,0x0035
    beq t0,zero,cc_have
    lw t9,-5816(t1)               # the engine's player
    lw t9,0x05CC(t7)              # the twin
cc_have:
    beq t9,zero,cc_go
    lui t1,0x004F
    sw t9,0x35A0(t1)              # 0x004F35A0: the cannon this camera looks along
cc_go:
    j 0x001589D0
    nop
"""
    code, _labels = assemble(BOSSV_AT, src, {})
    if "--cannon2view" in sys.argv:
        a = 0x00140C9C
        assert a not in result, "hook address already used: %08X" % a
        assert elf_word is None or elf_word(a) == 0x0C056274, "hook %08X: not the call of the cannon camera" % a
        result[a] = (3 << 26) | ((_labels["cn_cam"] >> 2) & 0x3FFFFFF)
        origin[a] = "own screens step 8 hook: the toy cannon's camera looks along the cannon of the camera's own hero"
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
old = "def add_boss_views(result, origin):" + NL
assert s.count(old) == 1
s = s.replace(old, "def add_boss_views(result, origin, elf_word=None):" + NL)
old = "        add_boss_views(result, origin)" + NL
assert s.count(old) == 1
s = s.replace(old, "        add_boss_views(result, origin, elf_word)" + NL)
u = "[--no-perview] [--plain] [--vopt=OPTION ...] [--cannon1view]"
assert s.count(u) == 1
s = s.replace(u, u + " [--cannon2view]")
with open(p, "w", encoding="utf-8", newline=chr(13) + chr(10)) as f:      # the file has CRLF line ends
    f.write(s)
print("ok")
