"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, FOURTH PART (option --holdshared): THE DOME ENDS ONCE (ninth round, the user's
items 1 and 4 of 2026-11-15 evening; STATE part 111).
SEEN (runs xsN / xsQ on candidate v124, player 2 reflecting in the laser dome): the dome's end ran TWICE in one frame (the
moves 0x107, 0x111, 0x112 twice on both heroes and Riku at 10450 .. 10454), and the heroes' success moves were cut to four
frames (with player 1 alone: 0x107 .. 0x112 over about 1,100 frames, runs xsO / xsM). READ (B_EX170_LAST): the hooked pieces
on a hero (the reflect, routine 8874; the laser hit, 7049) each step ask L7175 = "is this object the player (script call
1,309: the flag 0x80 at object + 0x588) AND has the dome's time run out"; then L7213 calls the laser end (script call 8,5)
and the success routine L7323. Both heroes carry the flag 0x80, so when both carry such a piece the end runs twice.
NOW (only with --holdshared; routines in co_two's room after co_two):
 le_note (the table word of the script call 8,5 = 0x00352BB0, was 0x001E0B98): the game's counter of the laser end is noted
   (0x000E7FB0), then the game's routine.
 ip_one (the table word of the script call 1,309 = 0x0034E6A8, was 0x00171090): the game's answer; for 4 steps after a
   laser end a "yes" becomes "no". So the end runs once, from whichever hero's piece asks first; nothing else changes
   (only the last Xemnas's script calls 8,5).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared5.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "le_note" in s:
    raise SystemExit("already there")

a = """(hs_hf, the first routine of co_two's room; run xsK: the dome came 60 steps after player 1's own green command).
"""
assert s.count(a) == 1
s = s.replace(a, a + """Its fourth part: the dome ends once (le_note notes the step of the laser end, script call 8,5; ip_one answers "not the
player", script call 1,309, for 4 steps after it; runs xsN / xsQ: with both heroes carrying a piece of the dome's script
the end ran twice in one frame).
""")

a = '''co_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""
'''
assert s.count(a) == 1
s = s.replace(a, '''co_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
le_note:                          # the script call (8,5) "the last Xemnas's laser end" (was 0x001E0B98): its step is noted
    lui t5,0x0035
    lw t6,-11076(t5)              # the game's counter
    lui t7,0x000E
    j 0x001E0B98
    sw t6,0x7FB0(t7)
ip_one:                           # the script call (1,309) "is the player" (was 0x00171090). a0 = its inputs; the answer is written to 0(a0)
    addiu sp,sp,-32
    sd ra,0(sp)
    jal 0x00171090
    sd a0,8(sp)
    ld a0,8(sp)
    lw t0,0(a0)                   # the game's answer
    beq t0,zero,ip_out
    lui t7,0x000E
    lw t1,0x7FB0(t7)              # the step of the last laser end (0 = none yet)
    beq t1,zero,ip_out
    lui t5,0x0035
    lw t2,-11076(t5)
    subu t2,t2,t1
    sltiu t2,t2,4
    beq t2,zero,ip_out
    nop
    sw zero,0(a0)                 # within 4 steps after it: "not the player", so the dome does not end a second time
ip_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""
''')

a = '''            hook_game(0x0034E228, 0x00174328, labels["co_two"], "the script call (1,165) 'command override': both heroes of a hold's pair")
'''
assert s.count(a) == 1
s = s.replace(a, a + '''            hook_game(0x00352BB0, 0x001E0B98, labels["le_note"], "the script call (8,5) 'last Xemnas laser end': its step is noted")
            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not for 4 steps after a laser end")
            n_glue += 2
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
