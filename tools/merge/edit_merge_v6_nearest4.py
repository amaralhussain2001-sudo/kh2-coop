"""One-off: tools/merge/merge_v6.py, twelfth glue (the nearer hero is "the player" for an object's thinking),
fourth version: while a scripted move holds the camera, the hero who is IN the move (bit 0x4000 of object +0x160;
tests z4-thorn-ev, b2-thorn) is "the player" for every object, whatever the distances. Seen in test b3-thorn:
the boss offered the move's follow-up command ("Break Raid") to the hero who stood nearer, not to the one in the
air."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "nr_dist2" in t:
    raise SystemExit("already there")
old = """nr_dist:
    lwc1 f0,0x70(a0)
"""
assert t.count(old) == 1
t = t.replace(old, """nr_dist:
    lui t3,0x0034
    lw t3,-13256(t3)              # 0x0033CC38: a scripted move (or a scene) holds the camera
    beq t3,zero,nr_dist2
    nop
    lw t3,0x160(t6)               # bit 0x4000: this hero is in a scripted move
    lw t2,0x160(t4)
    srl t3,t3,14
    srl t2,t2,14
    andi t3,t3,1
    andi t2,t2,1
    beq t3,t2,nr_dist2            # both or neither: the nearer one, as before
    nop
    bne t3,zero,nr_twin           # the twin is in the move: its follow-up commands are his
    nop
    b nr_body                     # player 1's hero is
    nop
nr_dist2:
    lwc1 f0,0x70(a0)
""")
old = "slot) is never taken: the other one is, whatever the distance."
assert t.count(old) == 1
t = t.replace(old, old + """ While a scripted move holds the camera
(0x0033CC38), the hero who is in the move (bit 0x4000 of object +0x160) is the player for every object, so
the move's follow-up commands go to him.""")
p.write_text(t, encoding="utf-8")
print("ok")
