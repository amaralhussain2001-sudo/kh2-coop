"""One-off: THE SEVENTY-SIXTH GLUE of tools/merge/merge_v7.py (--setposguard): trap_effect_set_pos ON AN ENDED EFFECT WRITES NOTHING
(tenth round; the user's words of 2026-11-16: "try to close everything now"; the Fortuneteller finding of STATE part 122).
SEEN (runs lbG / lbH on v132 and lbI on build 21, Agrabah's city al00 program 2, two heroes): 26 x "TLB Miss, pc=0x16e1a4 addr=0x0
[store]" when player 1's hero used the Fortuneteller's "Clear Shot".
READ (research of 2026-11-16, notes in the scratchpad's agentF folder): the handler 0x0016E180 is the script call trap_effect_set_pos
(0, 38) (the table 0x0034D8B0 holds 8-byte pairs; part 122's "(0, 76)" was the word index). Its first input is an effect handle:
0x001DC5F8(h) = h + 0x1C, the effect's body, which an effect's kill (0x001DC920) or end (0x001DC878) sets to 0. The Fortuneteller's
script M_EX620 sets the position of its crystal's effect each step (lines 244, 903, 3971) with no "is active" test, so after the
effect ended the 16-byte copy went to address 0 (the faulting store is the sq at 0x0016E1A8). PCSX2 drops that store; a real PS2
would take an exception. The same kind of fault as the one merge_v6.py's ep_guard closed for trap_effect_pos (0x0016E3C0).
THE GLUE (four words in place, no routine): 0x0016E19C beq v0,zero,0x0016E1B0 (an ended effect: nothing is written); 0x0016E1A4 beq
v0,t7,0x0016E1B0 (the game's own test); 0x0016E1A8 lq t0,0(t7); 0x0016E1AC sq t0,0(v0). The ld s0 in the first delay slot restores
s0 on every path, as before. Whether the effect ends early only with two heroes is NOT known (the one-hero control did not reach
the moment); the guard is right either way.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_setposguard.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--setposguard" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-SIXTH GLUE (built only with the option --setposguard): trap_effect_set_pos (handler 0x0016E180) WRITES NOTHING FOR AN
ENDED EFFECT (its body pointer h + 0x1C is 0). Four words in place at 0x0016E19C .. 0x0016E1AC. Seen: the Fortuneteller's crystal
effect after "Clear Shot" (26 stores to address 0).

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

STEP = '''    if "--setposguard" in sys.argv:                                        # seventy-sixth glue (trap_effect_set_pos on an ended effect)
        assert game_word(0x0016E198) == 0x8E0F0004 and game_word(0x0016E1A0) == 0xDFB00000 and game_word(0x0016E1B0) == 0xDFBF0008
        for a, old, new, what in ((0x0016E19C, 0x104F0004, 0x10400004, "an ended effect (no body): nothing is written"),
                                  (0x0016E1A4, 0x79E80000, 0x104F0002, "the game's own test (the same vector)"),
                                  (0x0016E1A8, 0x7C480000, 0x79E80000, "the copy (read)"),
                                  (0x0016E1AC, 0xDFB00000, 0x7C480000, "the copy (write)")):
            hook_game(a, old, new, "trap_effect_set_pos: " + what)
        n_glue += 4

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
