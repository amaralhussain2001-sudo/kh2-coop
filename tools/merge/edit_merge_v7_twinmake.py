"""One-off: tools/merge/merge_v7.py gets the FIFTY-SIXTH GLUE (built only with --twinmake; an experiment for the
three one-hero small games): A SECOND HERO IS MADE AT RUN TIME where the room data have only one special hero
(the carpet escape's 0x05E9, the toy cannon 0x03C8, the sidecar's 0x0840). So no new disc would be needed.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_twinmake.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gw_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-SIXTH GLUE (built only with the option --twinmake; an experiment): A SECOND HERO MADE AT RUN TIME in the
three one-hero small games. Read: the build's identity rule (lane E, hook at the player factory 0x00179FD0)
makes "any other player object" the twin, and the game's "make an object" 0x0016F000(object number, place, turn)
goes through that factory.
gw_tick (the call at 0x00138538): when there is no twin, and the engine's player is the escape hero (0x05E9), the
  toy cannon (0x03C8) or the sidecar hero (0x0840), ONE more object of the same number is made 60 units beside
  him (0x000E7E6C the hero it was made for, 0x000E7E70 the object, 0x000E7E74 its class word).

'''
s = s.replace(a, hdr + a)
b = " [--sidecar2]"
assert s.count(b) == 1
s = s.replace(b, b + " [--twinmake]")

i = s.index("def main():")
src = '''# ---- fifty-sixth glue, an experiment (only with --twinmake) ------------------------------------------------
GW_AT = 0x000EBB00
GW_END = 0x000EBC00
GW_SRC = """
gw_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne t6,zero,wk_go             # there is one
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,wk_go
    lw t3,-5816(t5)               # the engine's player
    bne t3,t4,wk_go
    nop
    lw t2,8(t4)
    lw t2,0(t2)                   # his object number
    addiu t1,zero,0x05E9
    beq t2,t1,wk_make             # the escape hero
    addiu t1,zero,0x03C8
    beq t2,t1,wk_make             # the toy cannon
    addiu t1,zero,0x0840
    bne t2,t1,wk_go               # not the sidecar hero either
    nop
wk_make:
    lui t7,0x000E
    lw t1,0x7E6C(t7)
    bne t1,t4,wk_do               # another hero object than at the last try
    lw t9,0x7E70(t7)              # the object made at the last try
    beq t9,zero,wk_go             # (the try gave nothing: no second try for this hero)
    nop
    lw t1,0(t9)
    lw t0,0x7E74(t7)
    beq t1,t0,wk_go               # it is still there (and is not the twin: leave it)
    nop
wk_do:
    sw t4,0x7E6C(t7)
    sw zero,0x7E70(t7)
    addiu sp,sp,-48
    sd ra,0(sp)
    lwc1 f0,0x70(t4)
    lui t1,0x4270                 # 60.0
    mtc1 t1,f1
    add.s f0,f0,f1
    swc1 f0,16(sp)                # the hero's place, 60 units to the side
    lw t1,0x74(t4)
    sw t1,20(sp)
    lw t1,0x78(t4)
    sw t1,24(sp)
    lw t1,0x7C(t4)
    sw t1,28(sp)
    mtc1 zero,f12
    move a0,t2                    # the same object number
    jal 0x0016F000                # the game's own "make an object"; the build's identity rule makes it the twin
    addiu a1,sp,16
    beq v0,zero,wk_out
    lui t7,0x000E
    sw v0,0x7E70(t7)
    lw t1,0(v0)
    sw t1,0x7E74(t7)
wk_out:
    ld ra,0(sp)
    addiu sp,sp,48
wk_go:
    j TICK_NEXT
    move a0,zero
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--twinmake" in sys.argv:                                           # fifty-sixth glue, an experiment (a second hero made at run time)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GW_AT, GW_END, GW_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero made at run time in the three one-hero small games")
        hook_base(0x00138538, tick_next, jal(labels["gw_tick"]), "the field's START look-out: first, is a second special hero wanted")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
