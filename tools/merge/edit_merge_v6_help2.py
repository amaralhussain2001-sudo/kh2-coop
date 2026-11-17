"""One-off: tools/merge/merge_v6.py, thirteenth glue, second part: a helper that goes with the twin also THINKS
(0x0016A950, the twelfth glue's hook) with the twin's follow memory and the twin as the leader in the table."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "NEAR_HELP_SRC" in t:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''        code, labels = assemble(NEAR_AT, near_src, {})
''', '''        near_syms = {}
        if "--no-helpers" not in sys.argv:   # a helper that goes with the twin thinks with the twin's follow memory
            _c, hl = assemble(HELP_AT, HELP_SRC, {})
            near_syms = {k: hl[k] for k in ("hp_swap", "hp_table", "hp_full")}
            a0_, b0_ = "    beq t3,t2,nr_body             # a helper: unchanged", "    beq t3,t2,nr_help"
            if near_src.count(a0_) == 1:
                near_src = near_src.replace(a0_, b0_) + NEAR_HELP_SRC
        code, labels = assemble(NEAR_AT, near_src, near_syms)
''')
rep('''REACT_AT = 0x000F4A00''', '''NEAR_HELP_SRC = """
nr_help:                          # a helper thinks (a0). Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0x14(t7)                # the true member table, place 1
    bne a0,t3,nh_2
    lw t2,0x08(t7)
    bne t2,zero,nh_go
    nop
    b nr_body
    nop
nh_2:
    lw t3,0x18(t7)
    bne a0,t3,nr_body
    lw t2,0x0C(t7)
    beq t2,zero,nr_body
    nop
nh_go:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    jal nr_body
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
"""

REACT_AT = 0x000F4A00''')
rep('''    if "--no-helpers" not in sys.argv:
        elf = mips.Elf''', '''    if "--no-helpers" not in sys.argv and ("--no-nearest" in sys.argv or "--helper" in sys.argv):
        print("note: the helpers glue needs the 'an object thinks' hook of the nearest-hero glue; left out")
    elif "--no-helpers" not in sys.argv:
        elf = mips.Elf''')
rep('''helpers that go with him, then, when a helper goes with the twin, a second time with the twin as the leader, the''',
    '''helpers that go with him, then, when a helper goes with the twin, a second time with the twin as the leader, the''')
rep('''game's own behaviour, word for word.
''', '''game's own behaviour, word for word. A helper decides where to walk while HE thinks (0x0016A950), outside
those tasks, so the twelfth glue's hook does the same swap for a helper that goes with the twin (nr_help).
''')
p.write_text(t, encoding="utf-8")
print("ok")
