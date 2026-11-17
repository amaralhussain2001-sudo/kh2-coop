"""One-off: tools/own/make_release_test.py gets the variants 7 and 8: "blow" 0x00186888(hero, a zero vector) = the
script call (1,129) trap_obj_blow, the way a boss's script throws a held hero off. Run once."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "make_release_test.py"
s = p.read_text(encoding="utf-8")
assert "BLOW = " not in s
a = 'ACT0 = """'
assert s.count(a) == 1
s = s.replace(a, '''BLOW = """    sd zero,16(sp)
    sd zero,24(sp)
    ld a0,8(sp)
    jal 0x00186888                # "blow" (the script call (1,129)): he is thrown off, here with no speed
    addiu a1,sp,16
"""
''' + a)
a = "        6: CLEAR + NOMOTION + IDLE + ACT0}[variant]"
assert s.count(a) == 1
s = s.replace(a, "        6: CLEAR + NOMOTION + IDLE + ACT0, 7: BLOW, 8: DETACH + BLOW}[variant]")
a = "assert 0 < count < 0x8000 and 1 <= variant <= 6 and who in"
assert s.count(a) == 1
s = s.replace(a, "assert 0 < count < 0x8000 and 1 <= variant <= 8 and who in")
a = "  variant 6: variant 4, then the hero's action word (hero + 0x154) set to 0\n"
assert s.count(a) == 1
s = s.replace(a, a + "  variant 7: \"blow\" 0x00186888(hero, a zero vector)                                        (the script call \"blow\")\n"
                     "  variant 8: detach when he is attached, then variant 7\n")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
