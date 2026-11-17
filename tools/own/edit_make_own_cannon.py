"""One-off: tools/own/make_own.py gets the option --cannon1view (eighth round, an experiment for the toy cannon of
the vehicle items): while the engine's player is a toy cannon (object 0x03C8), ONE view is shown, as in a story
scene, so that both cannons are seen from behind in the one picture.
Why: run one4 (candidate v86, a second cannon made at run time): both cannons shoot, but player 2's own camera is
the normal follow camera and looks at his cannon from the front (`local\\tests\\r8one4-NM10_MS203-63\\p2_f006500.png`);
the cannon's own camera kind is set for camera 1 only (lane V1's notes: camera kinds act on player 1's camera).
Without the option the builder writes what it wrote before, bit for bit.
The record of the edit; run once:
  python -I tools/own/edit_make_own_cannon.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "make_own.py"
s = p.read_text(encoding="utf-8")
if "--cannon1view" in s:
    raise SystemExit("already there")
old = "    code, _labels = assemble(BOSSV_AT, BOSSV_SRC, {})" + NL
new = '''    src = BOSSV_SRC
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
    code, _labels = assemble(BOSSV_AT, src, {})
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
u = "[--no-perview] [--plain] [--vopt=OPTION ...]"
assert s.count(u) == 1
s = s.replace(u, u + " [--cannon1view]")
with open(p, "w", encoding="utf-8", newline=chr(13) + chr(10)) as f:      # the file has CRLF line ends
    f.write(s)
print("ok")
