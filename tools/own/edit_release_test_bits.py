"""One-off: tools/own/make_release_test.py gets the variants 9, 10, 11 (ninth round). Seen with hold_state_probe.py
(run dtA): the hero left in FC at the Dark Thorn is in the idle state (state object 0x0034EB60, as a free hero), is
not attached, but his motion part still has the captured motion (object + 0x154 = FC, + 0x15C = 2) and object +
0x160 has the bits 0x4000 and 0x0002 (later 0x0080 too), which a free hero has not. Run once."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "make_release_test.py"
s = p.read_text(encoding="utf-8")
assert "CLEAR2 = " not in s
a = 'ACT0 = """'
assert s.count(a) == 1
s = s.replace(a, '''CLEAR2 = """    ld a0,8(sp)
    lw t2,0x160(a0)
    addiu t1,zero,-16515          # not 0x4082
    and t2,t2,t1
    sw t2,0x160(a0)               # the bits 0x4000, 0x0080, 0x0002
    sw zero,0x240(a0)             # the captor word
    sw zero,0x15C(a0)             # the motion part's word + 0x1C
"""
''' + a)
a = "7: BLOW, 8: DETACH + BLOW}[variant]"
assert s.count(a) == 1
s = s.replace(a, "7: BLOW, 8: DETACH + BLOW,\n        9: CLEAR2 + NOMOTION + IDLE, 10: CLEAR2 + NOMOTION + IDLE + ACT0, 11: CLEAR2 + IDLE}[variant]")
a = "1 <= variant <= 8 and who in"
assert s.count(a) == 1
s = s.replace(a, "1 <= variant <= 11 and who in")
a = "  variant 8: detach when he is attached, then variant 7\n"
assert s.count(a) == 1
s = s.replace(a, a + "  variant 9: the bits 0x4000 / 0x0080 / 0x0002 of hero + 0x160, the captor word and hero + 0x15C cleared, then variant 1\n"
                     "  variant 10: variant 9, then the action word set to 0\n"
                     "  variant 11: the same clearing, then \"go idle\" alone\n")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
