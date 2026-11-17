"""One-off: tools/merge/merge_v7.py gets the SIXTIETH GLUE (built only with --holdwatch): NO HERO IS HELD FOR EVER.
What was there (eighth round, parts 81 and 82):
- At the Groundshaker (lk15 59, candidate v89) one step of the boss's hold landed on the free hero; he stood in
  the captured motion FE for the last 11,250 frames of the run. Nobody ends such a motion: the boss's script
  keeps "its" capture in its own work memory and is written for one hero.
- The fifty-ninth glue (--onevictim: "the capture goes to the hero this captor already holds") cured that run
  but MADE THE HYDRA WORSE (he18 171, candidate v92): its script captures the hero it chose again and again
  until he is captured; with every capture sent on to the other hero, that hero was captured every 60 frames
  from 14,980 to the end of the run. The fifty-ninth glue stays in the builder as a record; NO build uses it.
The rule now, without touching who a boss captures:
gy_tick (the call at 0x00138538, each step of the field): for player 1's hero and for the twin: he is in a
  captured motion (action FC .. FF) and it is THE SAME motion as at the step before: the steps are counted; at
  1,800 steps (30 seconds) of one and the same captured motion he is let go the game's own way ("no motion"
  0x0017EFA0(hero + 320, 0), then "go idle" 0x0016BD60(hero, 0), as the fiftieth glue's safety rule does).
  The longest single captured motion seen in the ten boss rooms that ended by itself was shorter than 700
  steps; a whole hold (several motions in a row) was at most 1,082.
State: 0x000E7E78 / 7C (player 1's hero: the motion seen, its steps), 0x000E7E80 / 84 (the twin's).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdwatch.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gy_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTIETH GLUE (built only with the option --holdwatch): NO HERO IS HELD FOR EVER. A boss's script is written for
one hero; with two, a step of a hold can land on the free hero and nobody ends it (the Groundshaker: a hero in
the captured motion FE for 11,250 frames). gy_tick (the call at 0x00138538): a hero who is in ONE AND THE SAME
captured motion (action FC .. FF) for 1,800 steps is let go the game's own way (0x0017EFA0, 0x0016BD60). Who a
boss captures is not touched (the fifty-ninth glue tried that and made the Hydra worse; no build uses it).

'''
s = s.replace(a, hdr + a)
b = " [--onevictim]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--holdwatch]")

i = s.index("def main():")
src = '''# ---- sixtieth glue (only with --holdwatch) ------------------------------------------------------------------
GY_AT = 0x000EC000
GY_END = 0x000EC100
GY_LIMIT = 1800                                    # steps of one and the same captured motion before the hero is let go
GY_SRC = """
gy_tick:                          # from 0x00138538 (the field's START look-out, each step)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui t5,0x0035
    lw a0,-5816(t5)               # the engine's player = player 1's hero
    lui s0,0x000E
    jal gy_one
    ori s0,s0,0x7E78              # his two words
    lui t7,0x000F
    lw a0,0x05CC(t7)              # the twin
    jal gy_one
    addiu s0,s0,8
    ld s0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
    j TICK_NEXT
    move a0,zero

gy_one:                           # a0 = a hero (or 0), s0 = his two words: the captured motion seen, the steps it has lasted
    beq a0,zero,gy_clr
    nop
    lw t2,0x154(a0)
    andi t2,t2,0xFFFF
    andi t1,t2,0xFFFC
    addiu t0,zero,0x00FC
    bne t1,t0,gy_clr              # he is in no captured motion
    lw t3,0(s0)
    bne t3,t2,gy_new              # another captured motion than at the step before
    lw t4,4(s0)
    addiu t4,t4,1
    slti t1,t4,@LIMIT@
    bne t1,zero,gy_keep
    sw t4,4(s0)
    sw zero,4(s0)                 # ONE AND THE SAME captured motion for all these steps: nobody ends it. He is let go
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion": the captured motion ends
    move a1,zero
    ld a0,8(sp)
    jal 0x0016BD60                # "go idle": his action is ended the game's own way
    move a1,zero
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gy_new:
    sw t2,0(s0)
    jr ra
    sw zero,4(s0)
gy_clr:
    sw zero,0(s0)
    jr ra
    sw zero,4(s0)
gy_keep:
    jr ra
    nop
""".replace("@LIMIT@", str(GY_LIMIT))


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--holdwatch" in sys.argv:                                          # sixtieth glue (no hero is held for ever)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GY_AT, GY_END, GY_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "a hero in one and the same captured motion for 1,800 steps is let go")
        hook_base(0x00138538, tick_next, jal(labels["gy_tick"]), "the field's START look-out: first, is a hero held too long")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
