"""One-off: the SIXTY-FIFTH GLUE of tools/merge/merge_v7.py (--holdpair), second form: its piece inside the
forty-seventh glue ("both heroes of a pair may press the captor's command, once a step") made that glue one word
too long for its room (129 of 128). The piece is now the routine hp_rc in the sixty-fifth glue's own room, and
the forty-seventh glue's rc_drop2 only jumps to it.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdpair2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hp_rc:" in s:
    raise SystemExit("already there")

# (1) the long piece inside the forty-seventh glue becomes a jump
a = s[s.index('                rc_src = rc_src.replace(x, """rc_drop2:\n    lui t7,0x000E\n    lw t2,0x7EA0(t7)'):]
a = a[:a.index('""")\n') + len('""")\n')]
assert s.count(a) == 1 and "rc_drop3" in a
b = '''                rc_src = rc_src.replace(x, """rc_drop2:
    j HP_RC                       # (--holdpair) the sixty-fifth glue's hp_rc: both heroes of a hold's pair may press
    nop
""")
'''
s = s.replace(a, b)

# (2) the forty-seventh glue is assembled with the address of hp_rc; the address of its rc_send is kept
a = '''        labels, n = add_code(RC_AT, RC_END, rc_src, {}, "a hero's Reaction Command: the sender is the player; one object holds one hero")
'''
assert s.count(a) == 1
b = '''        rc_syms = {}
        if "--holdpair" in sys.argv:
            _c, hp_l = assemble(HP_AT, HP_SRC.replace("@STUBS@", hp_stubs()), {"TICK_NEXT": 0, "CAP_NEXT": 0, "RC_SEND": 0})
            rc_syms["HP_RC"] = hp_l["hp_rc"]
        labels, n = add_code(RC_AT, RC_END, rc_src, rc_syms, "a hero's Reaction Command: the sender is the player; one object holds one hero")
        rc_send_at = labels["rc_send"]
'''
s = s.replace(a, b)

# (3) the stubs as a function; hp_rc in the sixty-fifth glue
a = '''        stubs = ""
        for num, tab, fn, kind in HP_TRAPS:
            stubs += "hp_t%d:\\n    lui t0,0x%04X\\n    j hp_mir%s\\n    ori t0,t0,0x%04X\\n" % (num, fn >> 16, kind, fn & 0xFFFF)
        labels, n = add_code(HP_AT, HP_END, HP_SRC.replace("@STUBS@", stubs),
                             {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "CAP_NEXT": (cap_next & 0x3FFFFFF) << 2},
'''
assert s.count(a) == 1, s.count(a)
b = '''        labels, n = add_code(HP_AT, HP_END, HP_SRC.replace("@STUBS@", hp_stubs()),
                             {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "CAP_NEXT": (cap_next & 0x3FFFFFF) << 2, "RC_SEND": rc_send_at},
'''
s = s.replace(a, b)
a = "def main():" + NL
assert s.count(a) == 1
b = '''def hp_stubs():
    """The sixty-fifth glue's entry for each wrapped script call: the game's handler in t0, then the mirror routine."""
    stubs = ""
    for num, tab, fn, kind in HP_TRAPS:
        stubs += "hp_t%d:\\n    lui t0,0x%04X\\n    j hp_mir%s\\n    ori t0,t0,0x%04X\\n" % (num, fn >> 16, kind, fn & 0xFFFF)
    return stubs


def main():
'''
s = s.replace(a, b)
a = '''hp_note:                          # in: a0 = a hero (or 0), a1 = 1 (the twin) / 2 (player 1's).'''
assert s.count(a) == 1
b = '''hp_rc:                            # jump from the forty-seventh glue's rc_drop2 ("this hero's command does nothing"): a0 = the source, a1 = the hero, t5 = 0x00350000
    lui t7,0x000E
    lw t2,0x7EA0(t7)              # both heroes are in this captor's hold: either may press, once a step
    beq t2,zero,hr_drop
    lw t1,0x7EA8(t7)
    bne t1,a0,hr_drop
    lw t1,0x7EA4(t7)
    beq t2,a1,hr_pair
    nop
    bne t1,a1,hr_drop
    nop
hr_pair:
    lw t2,0x7C1C(t7)              # the step of the last command that was sent
    lw t1,-11076(t5)
    beq t2,t1,hr_drop
    nop
    j RC_SEND
    nop
hr_drop:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop

'''
s = s.replace(a, b + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
