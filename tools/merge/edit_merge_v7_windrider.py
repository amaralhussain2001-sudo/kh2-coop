r"""One-off (STATE part 145; the user's words 2026-11-18: "finish the 11 9 8 for now", item 11 (a) = the whirlwinds per rider):
THE EIGHTY-SECOND GLUE, option --windrider. Research: local\analysis\agent-rides\rides-design.txt (read-only agent).
The whirlwind (F_MU070 0x0151 in the Land of Dragons square, F_MU070_BOSS 0x0457 in the Storm Rider fight; one script): its command
33 "Ride the Wind" hooks a script piece on the hero who pressed it (his hooked context hero+0xAEC); the piece captures him (0xFC)
and waits for trap_pad_is_trigger(8) (0x0016DBE0), which reads BOTH controllers since the sixteenth glue (pad_both), so player 1's
Cross threw player 2 out of his whirlwind (r27-wind-p1x).
Now rw_pad sits at the two script button tests (0x0016DBA8 'held', 0x0016DBF0 'pressed'; were jal pad_both): when the running
script piece (0x0034D8A4) belongs to a whirlwind object and is the hooked context of one hero, that hero's own controller record
answers (0x0034D6C0 player 1, 0x0034D720 player 2), unless the sixty-fifth glue's pair holds both heroes in this very whirlwind
(then one script drives both: either controller, as before). Everything else: pad_both, as before (ra kept, so po_pad still
knows the caller). Without --windrider the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_windrider.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--windrider" in t:
    raise SystemExit("already done")

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTY-SECOND GLUE (built only with the option --windrider): EACH WHIRLWIND RIDER'S OWN BUTTON. rw_pad (the script button tests
0x0016DBA8 'held' and 0x0016DBF0 'pressed', were jal pad_both): when the running script piece (0x0034D8A4) has a whirlwind object
(0x0151 F_MU070, 0x0457 F_MU070_BOSS) and is one hero's hooked context (hero + 0xAEC: the piece of "Ride the Wind"), only that hero's
controller record answers; when the sixty-fifth glue's pair holds the other hero in the same whirlwind (0x000E7EA0/A4/A8 and his
+0x160 bit 0x4000), both controllers (one script drives both). Everything else goes on to pad_both. Room 0x000DE480 .. 0x000DE580.
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eighty-second glue (only with --windrider) ------------------------------------------------------------------
RW_AT = 0x000DE480
RW_END = 0x000DE580
RW_HOOKS = (0x0016DBA8, 0x0016DBF0)               # the script tests 'held' / 'pressed' (jal pad_both since the sixteenth glue)
RW_SRC = """
rw_pad:                           # a script's button test (a0 = 0 in the delay slot); returns v0 = a controller record
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,rw_both
    lui t5,0x0035
    lw t5,-10076(t5)              # the running script piece (0x0034D8A4)
    beq t5,zero,rw_both
    nop
    lw t4,56(t5)                  # its object
    srl t3,t4,22
    addiu t3,t3,-6
    bne t3,zero,rw_both           # not an object
    nop
    lw t3,8(t4)
    lw t3,0(t3)                   # the object's number
    addiu t2,zero,0x0151          # F_MU070, the whirlwind of the Land of Dragons square
    beq t3,t2,rw_wind
    addiu t2,zero,0x0457          # F_MU070_BOSS, the whirlwinds of the Storm Rider fight
    bne t3,t2,rw_both
    nop
rw_wind:
    lw t2,0xAEC(t6)               # the twin's hooked piece
    beq t2,t5,rw_twin
    lui t3,0x0035
    lw t3,0x2400(t3)              # player 1's hero (0x00352400)
    beq t3,zero,rw_both
    nop
    lw t2,0xAEC(t3)
    bne t2,t5,rw_both             # the piece of neither hero: as before
    move t1,t6                    # the other hero: the twin
    lui v0,0x0035
    b rw_pair
    addiu v0,v0,-10560            # player 1's controller record (0x0034D6C0)
rw_twin:
    lui t1,0x0035
    lw t1,0x2400(t1)              # the other hero: player 1's
    lui v0,0x0035
    addiu v0,v0,-10464            # player 2's controller record (0x0034D720)
rw_pair:                          # a shared ride (the sixty-fifth glue's pair in this whirlwind, the other hero held)?
    beq t1,zero,rw_own
    lui t9,0x000E
    lw t8,0x7EA8(t9)              # the pair's captor
    bne t8,t4,rw_own
    lw t8,0x7EA0(t9)
    beq t8,t1,rw_held
    lw t8,0x7EA4(t9)
    bne t8,t1,rw_own
    nop
rw_held:
    lw t8,0x160(t1)
    andi t8,t8,0x4000
    bne t8,zero,rw_both           # both heroes ride this whirlwind: either controller
    nop
rw_own:
    jr ra
    nop
rw_both:
    j 0x000F4740                  # pad_both (the second glue; po_pad sees ra 0x0016DBB0 / 0x0016DBF8)
    nop
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--windrider" in sys.argv:                                          # eighty-second glue (each whirlwind rider's button)
        code, labels = assemble(RW_AT, RW_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert RW_AT + 4 * len(code) <= RW_END, "the eighty-second glue does not fit"
        clash = [a for a in words if RW_AT <= a < RW_END]
        assert not clash, "patch words in 0x000DE480 .. 0x000DE57F: %08X" % clash[0]
        for i, w in enumerate(code):
            a = RW_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (each whirlwind rider's own button)"
        for a in RW_HOOKS:
            hook_base(a, 0x0C03D1D0, jal(labels["rw_pad"]), "a script's button test: a whirlwind rider's own controller, else pad_both")
        n_glue += len(code)

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-second glue (--windrider) added")
