"""One-off: tools/merge/merge_v6.py, twelfth glue, fifth version: while a scripted move holds the camera and the
TWIN is the hero in it, the twin's own thinking sees the twin as "the player". Seen in tests b5-thorn-nopress /
b6-thorn-p1press: the follow-up command of the twin's move ("Break Raid") was put on player 1's menu and only
player 1's Triangle started it; the hero's own script offers it and asks for "the player"."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "nr_self" in t:
    raise SystemExit("already there")
old = """    beq a0,t6,nr_body
    lw t3,0(a0)
"""
assert t.count(old) == 1
t = t.replace(old, """    beq a0,t6,nr_self
    lw t3,0(a0)
""")
old = """nr_dist:
    lui t3,0x0034
"""
assert t.count(old) == 1
t = t.replace(old, """nr_self:                          # the twin thinks. In a scripted move that holds the camera he is "the player"
    lui t3,0x0034                 # of his own script (the move's follow-up commands are offered by it)
    lw t3,-13256(t3)
    beq t3,zero,nr_body
    lw t3,0x160(t6)
    srl t3,t3,14
    andi t3,t3,1
    bne t3,zero,nr_twin
    nop
    b nr_body
    nop
""" + old)
old = "the move's follow-up commands go to him."
assert t.count(old) == 1
t = t.replace(old, old + """ In such a move the twin's own thinking also sees the twin as the player (nr_self):
his own script offers the follow-up commands.""")
p.write_text(t, encoding="utf-8")
print("ok")
