"""One-off: tools/merge/merge_v7.py gets an EXPERIMENT for plan row 9's second half, built only with --together:
when an enemy or a boss pulls ONE hero into a paired move and the OTHER hero is up and near (800 units), the same
move is started on the other hero too (a second call of the game's paired-move routine). It is the test "what
happens when both heroes are in a boss's move": do they stand inside each other, does the second one get free.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tg_cap" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTIETH GLUE, AN EXPERIMENT (NOT in any build; built only with the option --together): BOTH HEROES IN A BOSS'S
PAIRED MOVE (plan row 9, second half; the user's decision of 2026-11-10 "try both together").
Read in the program: the paired-move routine 0x00180378(captor's motion part = captor + 0x140, victim, motion
number, time) starts the victim's part of the move with 0x001801B0 -> 0x00180058, which writes the CAPTOR OBJECT
into the victim's motion part (+ 0xFC) and counts the victim in the captor's word + 0x488. So the victim's place
comes from the captor, and a second victim is one more call with the other hero.
tg_cap (the jump at 0x00180378): when the captor is an object that is neither a hero nor a helper, the victim is
a hero, and the OTHER hero is up and less than 800 units from the captor, the routine is called once more for the
other hero with the same motion (a busy flag at 0x000E7E30 stops the second call from doing it again).
NOT together with the test recorders that sit on 0x00180378 (the kits -cap).

'''
s = s.replace(a, hdr + a)
b = "[--ownrec [--ownmenu]]"
assert s.count(b) == 1
s = s.replace(b, b + " [--together]")
i = s.index("def main():")
src = '''# ---- fiftieth glue, an experiment (only with --together) --------------------------------------------------
TG_AT = 0x000E9C00
TG_END = 0x000E9E00
TG_SRC = """
tg_cap:                           # jump at 0x00180378 (its first two instructions are at tg_go). a0 = the captor's
    lui t7,0x000E                 # motion part, a1 = the victim, a2 = the motion number, f12 = the time
    lw t6,0x7E30(t7)
    bne t6,zero,tg_go             # this IS the second call
    lui t5,0x000F
    lw t6,0x05CC(t5)              # the twin
    beq t6,zero,tg_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tg_go
    nop
    beq a1,t6,tg_o                # the victim is the twin: the other hero is player 1's
    move t3,t4
    bne a1,t4,tg_go               # the victim is no hero
    move t3,t6
tg_o:
    addiu t8,a0,-320              # the captor object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,tg_go             # not an object
    nop
    beq t8,t4,tg_go               # a hero or a helper holds (a Limit ...): as the game
    nop
    beq t8,t6,tg_go
    lw t2,0(t8)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,tg_go
    nop
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tg_go
    nop
    lw t2,0(t2)
    beq t2,zero,tg_go             # he is down
    nop
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # his distance to the captor, squared
    lui t2,0x491C
    ori t2,t2,0x4000              # 640000.0 = 800 units, squared
    mtc1 t2,f4
    c.lt.s f2,f4
    bc1f tg_go                    # too far: he stays free
    nop
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,40(sp)
    swc1 f12,32(sp)
    addiu t2,zero,1
    sw t2,0x7E30(t7)
    jal 0x00180378                # the same move on the other hero
    move a1,t3
    lui t7,0x000E
    sw zero,0x7E30(t7)
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f12,32(sp)
    addiu sp,sp,64
tg_go:
    addiu sp,sp,-48               # the two instructions that sat at 0x00180378
    j 0x00180380
    swc1 f20,32(sp)
"""
TG_HOOK = (0x00180378, 0x27BDFFD0, 0xE7B40020)     # addiu sp,sp,-48 / swc1 f20,32(sp)


'''
s = s[:i] + src + s[i:]
e = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(e) == 1
step = '''    if "--together" in sys.argv:                                           # fiftieth glue, an experiment (plan row 9, second half)
        labels, n = add_code(TG_AT, TG_END, TG_SRC, {}, "EXPERIMENT: a boss's paired move is started on the other hero too when he is near")
        a, w0, w1 = TG_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["tg_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first tg_cap")
        hook_game(a + 4, w1, 0, "(swc1 f20,32(sp) is done in tg_go)")
        n_glue += n + 2

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
