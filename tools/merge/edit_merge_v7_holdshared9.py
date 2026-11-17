"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, FIFTH PART (option --holdshared): ONLY AN ENEMY'S GRAB IS SINGLE-TARGET; ANY OTHER
CAPTOR (A BOARD, A GIMMICK) PAIRS AS IN BUILD 20 (ninth round; STATE part 115).
WHY: the whole regression of v128 (prefix b26) has 9 flagged runs with 49 / 50 fault lines each: Mail Delivery (b26-mail,
k9-mailend), the six skateboard challenges (k9-skate-*) and the skate retry (b12-skate-retry); build 20's regression had 0.
Bisect (the skate run on test-v4-al109, hidden, sandboxes run-x7 .. run-x10): v118, v120, v121 = 0; v122 (the fifth form's
first part) = 49; variants vA (v122's options with glue 68 and the fourth form) and vB (no glue 68, the fourth form) = 0. So
the fifth form is the cause. Capture log (runs k9c-skate-v128-cap / -vB-cap): at frame 5120 the object 0x01A8D420 (its
script runs with player 2 as "the player") captures PLAYER 1'S hero with 0xFC; build 20's pair rule put player 2's hero
into the same hold and the game ended clean; with the fifth form only player 1's hero is taken and the game's end then
works on an empty object (pc 0x0017EBC8 .. 0x0017F380, addresses 0x140 .. 0x288). The user's rule is about BOSSES' grabs.
NOW (only with --holdshared):
 hs_kind (fixed entry CO_AT + 16, from hp_form in place of the shared-mechanic test): the captor's kind (its object entry
   + 4, the byte of 00objentry: BOSS 3, ZAKO 4, E_WEAPON 6, L_BOSS 12, L_ZAKO 21, E_OBJ 23 = an enemy): an enemy's capture
   makes a pair only for the last Xemnas's laser dome (move 0x106, captor 0x081F / 0x09CA); ANY OTHER CAPTOR makes the pair
   of build 20 (the fourth form). The test leaves glue 65's range (12 words less there).
 co_two and hs_rc act only while the pair's captor (0x000E7EA8) is 0x081F or 0x09CA (the dome): a pair of any other captor
   is build 20's (no second offer, each player's press in his own name).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared9.py"""
import pathlib

NL = chr(10)
BS = chr(92)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hs_kind" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)


n = BS + "n"
old = ("    addiu t1,zero,0x106           # (--holdshared) ONLY A SHARED MECHANIC: the last Xemnas's laser dome" + n +
       "    bne a3,t1,hf_no" + n +
       "    lw t2,8(a1)                   # the captor's object entry" + n +
       "    beq t2,zero,hf_no" + n +
       "    nop" + n +
       "    lw t2,0(t2)                   # its object number" + n +
       "    addiu t1,zero,0x081F" + n +
       "    beq t2,t1,hf_sh" + n +
       "    addiu t1,zero,0x09CA" + n +
       "    bne t2,t1,hf_no" + n +
       "    nop" + n +
       "hf_sh:")
new = ("    j 0x000EE4D0                  # (--holdshared) hs_kind: an enemy pairs only for the laser dome, another captor as build 20" + n +
       "    nop" + n +
       "hf_sh:")
rep(old, new)

rep("""Its fourth part: the dome's pieces run on ONE hero, PLAYER 1'S, the one its lasers aim at, as in the game (runs xsN / xsQ:""",
    """Its fifth part: ONLY AN ENEMY'S GRAB is single-target (the captor's kind, object entry + 4: BOSS 3, ZAKO 4, E_WEAPON 6,
L_BOSS 12, L_ZAKO 21, E_OBJ 23); any other captor (a board, a gimmick) pairs as in build 20, and co_two / hs_rc act only in
the dome (the regression of v128: Mail Delivery and the skate challenges ended with 49 fault lines without build 20's pair).
Its fourth part: the dome's pieces run on ONE hero, PLAYER 1'S, the one its lasers aim at, as in the game (runs xsN / xsQ:""")

rep('''co_e2:
    j hs_rc
    nop
''', '''co_e2:
    j hs_rc
    nop
co_e3:                            # CO_AT + 16 from hp_form, in place of the shared-mechanic test
    j hs_kind
    nop
''')

rep('''hs_rc:                            # from hp_rc: a command of PLAYER 2'S hero in the pair is sent in PLAYER 1'S hero's name (a1 = the hero)
    lui t7,0x000F
''', '''hs_kind:                          # a0 = the victim, a1 = the captor, a3 = the move; t1 / t2 free. -> HF_SH (a pair) or HF_NO
    lw t2,8(a1)                   # the captor's object entry
    beq t2,zero,hk_pair           # none: as build 20
    nop
    lbu t1,4(t2)                  # its kind (00objentry + 4)
    addiu t2,zero,3               # BOSS
    beq t1,t2,hk_enemy
    addiu t2,zero,4               # ZAKO
    beq t1,t2,hk_enemy
    addiu t2,zero,6               # E_WEAPON
    beq t1,t2,hk_enemy
    addiu t2,zero,12              # L_BOSS
    beq t1,t2,hk_enemy
    addiu t2,zero,21              # L_ZAKO
    beq t1,t2,hk_enemy
    addiu t2,zero,23              # E_OBJ
    bne t1,t2,hk_pair             # not an enemy (a board, a gimmick, ...): the pair of build 20
    nop
hk_enemy:                         # an enemy's grab: a pair only for the shared mechanic, the last Xemnas's laser dome
    addiu t1,zero,0x106
    bne a3,t1,hk_no
    lw t2,8(a1)
    lw t2,0(t2)                   # the captor's object number
    addiu t1,zero,0x081F
    beq t2,t1,hk_pair
    addiu t1,zero,0x09CA
    bne t2,t1,hk_no
    nop
hk_pair:
    j HF_SH
    nop
hk_no:
    j HF_NO
    nop
hs_rc:                            # from hp_rc: a command of PLAYER 2'S hero in the DOME's pair is sent in PLAYER 1'S hero's name (a1 = the hero)
    lui t7,0x000E
    lw t1,0x7EA8(t7)              # the pair's captor: only the laser dome's boss
    beq t1,zero,hs_rc2
    nop
    lw t1,8(t1)
    beq t1,zero,hs_rc2
    nop
    lw t1,0(t1)
    addiu t2,zero,0x081F
    beq t1,t2,hs_rc1
    addiu t2,zero,0x09CA
    bne t1,t2,hs_rc2
    nop
hs_rc1:
    lui t7,0x000F
''')

rep('''    lw t0,0x7EA0(t7)              # a living pair of the sixty-fifth glue (with --holdshared: only the laser dome)
    beq t0,zero,co_out
    lw t1,0x7EA4(t7)
    beq t1,zero,co_out
''', '''    lw t0,0x7EA0(t7)              # a living pair of the sixty-fifth glue
    beq t0,zero,co_out
    lw t1,0x7EA4(t7)
    beq t1,zero,co_out
    lw t2,0x7EA8(t7)              # its captor: only the last Xemnas's laser dome (0x081F / 0x09CA)
    beq t2,zero,co_out
    nop
    lw t2,8(t2)
    beq t2,zero,co_out
    nop
    lw t2,0(t2)
    addiu t3,zero,0x081F
    beq t2,t3,co_dome
    addiu t3,zero,0x09CA
    bne t2,t3,co_out
    nop
co_dome:
''')

rep('''            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"], "RC_SEND": rc_send_at},''',
    '''            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"], "RC_SEND": rc_send_at, "HF_SH": labels["hf_sh"], "HF_NO": labels["hf_no"]},''')
rep('''            assert labels["co_e2"] == CO_AT + 8 and labels["hs_hf"] > CO_AT + 8
''', '''            assert labels["co_e2"] == CO_AT + 8 and labels["co_e3"] == CO_AT + 16 and labels["hs_hf"] > CO_AT + 16
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
