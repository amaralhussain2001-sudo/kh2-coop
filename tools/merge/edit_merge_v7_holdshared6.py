"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, FOURTH PART, SECOND FORM (option --holdshared): THE DOME'S PIECES RUN ON ONE HERO
(ninth round, the user's items 1 and 4 of 2026-11-15 evening; STATE part 111).
WHY: the first form (edit_merge_v7_holdshared5.py: le_note + ip_one "not the player for 4 steps after a laser end") is WRONG:
run xsS on v125 (presses five frames apart) has ONE FAULT LINE "TLB Miss, pc=0x1e2ac0 addr=0xdc0 [store]": pc 0x001E2AC0 is
the game's laser-end routine; the second hero's piece of the dome's script waited out the 4 steps and ended the dome a
second time (counter 10454, four steps after the first), when the laser object was gone. (On v124 the two ends came in
the same frame and did not fault; the heroes' success moves were cut short.)
READ (B_EX170_LAST): the reflect callback (L8623) hooks the reflect piece (8874) onto THE HERO WHO SENT the command; the
hit piece (7049) goes onto the hero a laser hits; both pieces end the dome (L7175 -> L7213) when their hero "is the player"
(script call 1,309: flag 0x80 at object + 0x588; both heroes carry it). In the one-hero game all pieces run on one hero.
NOW (only with --holdshared):
 hs_rc (fixed entry CO_AT + 8, from hp_rc in place of its "j RC_SEND"): while a pair of glue 65 lives (with --holdshared
   only the dome makes one), a command of the pair's OTHER hero (0x000E7EA4) is sent in the NAMED hero's name (0x000E7EA0):
   the boss's script hooks its reflect piece onto the named hero, the mirror gives the move to the other hero, the boss's
   count goes up once. Each player's press still counts (once a step, hp_rc).
 ip_one (the script call 1,309, table word 0x0034E6A8), second form: while that pair lives and the other hero is held
   (bit 0x4000 of + 0x160), he is "not the player" for the boss's script (a safety net: if a laser hits him directly, his
   hit piece does not end the dome a second time). After the dome, when he is free, the game's answer as always.
 le_note and its table word (0x00352BB0, the script call 8,5) are taken out again: the game's own routine.
 CO_SRC starts with two fixed entries: CO_AT + 0 "j hs_hf" (hp_form jumps there), CO_AT + 8 "j hs_rc" (hp_rc jumps there).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared6.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hs_rc" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("""Its fourth part: the dome ends once (le_note notes the step of the laser end, script call 8,5; ip_one answers "not the
player", script call 1,309, for 4 steps after it; runs xsN / xsQ: with both heroes carrying a piece of the dome's script
the end ran twice in one frame).
""", """Its fourth part: the dome's pieces run on ONE hero, as in the game (runs xsN / xsQ: with both heroes carrying a piece of the
dome's script the end ran twice; xsS: a second end four steps late faulted at 0x001E2AC0): hs_rc sends a press of the
pair's other hero in the named hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press), and ip_one (script call 1,309) answers "not the player" for the other hero while he is held in the pair.
""")

rep('''CO_SRC = """
hs_hf:                            # (--holdshared) from hp_form's hf_h (MUST stay the first routine: hp_form jumps to CO_AT)
''', '''CO_SRC = """
co_e1:                            # (--holdshared) FIXED ENTRIES: CO_AT + 0 from hp_form's hf_h, CO_AT + 8 from hp_rc
    j hs_hf
    nop
co_e2:
    j hs_rc
    nop
hs_hf:                            # the laser dome is never a hero's own move
''')

rep('''le_note:                          # the script call (8,5) "the last Xemnas's laser end" (was 0x001E0B98): its step is noted
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
''', '''hs_rc:                            # from hp_rc: a command of the pair's OTHER hero is sent in the NAMED hero's name (a1 = the hero)
    lui t7,0x000E
    lw t1,0x7EA4(t7)              # the pair's other hero
    bne a1,t1,hs_rc2
    nop
    lw a1,0x7EA0(t7)              # the named hero: the boss's pieces of the dome run on him, as in the game
hs_rc2:
    j RC_SEND
    nop
ip_one:                           # the script call (1,309) "is the player" (was 0x00171090). a0 = its inputs: 0(a0) = the object; the answer is written there
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    lw t0,0(a0)                   # the object asked about
    jal 0x00171090
    sd t0,16(sp)
    ld a0,8(sp)
    lui t7,0x000E
    lw t1,0x7EA0(t7)              # a living pair (with --holdshared: the laser dome)
    beq t1,zero,ip_out
    lw t1,0x7EA4(t7)              # its other hero
    ld t0,16(sp)
    bne t0,t1,ip_out
    nop
    lw t2,0x160(t0)
    andi t2,t2,0x4000
    beq t2,zero,ip_out            # he is free: the game's answer
    nop
    sw zero,0(a0)                 # held in the pair: he is not "the player" of the boss's script (its pieces and its end stay with the named hero)
ip_out:
''')

rep('''            hook_game(0x00352BB0, 0x001E0B98, labels["le_note"], "the script call (8,5) 'last Xemnas laser end': its step is noted")
            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not for 4 steps after a laser end")
            n_glue += 2
''', '''            assert labels["co_e2"] == CO_AT + 8 and labels["hs_hf"] > CO_AT + 8
            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not the pair's other hero while he is held")
            n_glue += 1
''')

rep('''            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"]},''',
    '''            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"], "RC_SEND": rc_send_at},''')

a = '''    _o = "hf_h:\\n    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone\\n"
'''
assert s.count(a) == 1
s = s.replace(a, '''    _o2 = "    j RC_SEND\\n    nop\\nhr_drop:\\n"
    assert HP_SRC.count(_o2) == 1
    HP_SRC = HP_SRC.replace(_o2, "    j 0x000EE4C8                  # (--holdshared) hs_rc: the other hero's press in the named hero's name\\n    nop\\nhr_drop:\\n")
''' + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
