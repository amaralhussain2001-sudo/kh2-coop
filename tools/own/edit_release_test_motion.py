"""One-off: tools/own/make_release_test.py gets the variants 12, 13, 14 (ninth round): "motion start"
0x0017F488(hero + 320, motion, 0.0) = the script call (1,11), as the Dark Thorn's own script does before it throws
the hero ("motion start 16", then "blow"). Run once."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "make_release_test.py"
s = p.read_text(encoding="utf-8")
assert "MSTART" not in s
a = 'ACT0 = """'
assert s.count(a) == 1
s = s.replace(a, '''MSTART = """    ld a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017F488                # "motion start" (the script call (1,11))
    addiu a1,zero,@M@
"""
''' + a)
a = "11: CLEAR2 + IDLE}[variant]"
assert s.count(a) == 1
s = s.replace(a, '11: CLEAR2 + IDLE,\n        12: MSTART.replace("@M@", "0") + CLEAR2 + IDLE, 13: MSTART.replace("@M@", "16") + BLOW,\n'
                 '        14: CLEAR2 + MSTART.replace("@M@", "16") + BLOW}[variant]')
a = "1 <= variant <= 11 and who in"
assert s.count(a) == 1
s = s.replace(a, "1 <= variant <= 14 and who in")
a = "  variant 11: the same clearing, then \"go idle\" alone\n"
assert s.count(a) == 1
s = s.replace(a, a + "  variant 12: \"motion start 0\", the clearing of variant 9, \"go idle\"\n"
                     "  variant 13: \"motion start 16\", then \"blow\" (the Dark Thorn's own throw)\n"
                     "  variant 14: the clearing of variant 9, then variant 13\n")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
