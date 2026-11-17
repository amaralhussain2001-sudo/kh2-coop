"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, FOURTH PART, THIRD FORM (option --holdshared): THE DOME'S PIECES RUN ON PLAYER 1'S
HERO, THE ONE THE LASERS AIM AT (ninth round, the user's items 1 and 4 of 2026-11-15 evening; STATE part 113).
WHY: the second form (edit_merge_v7_holdshared6.py) sent the other hero's press in the NAMED hero's name. Run xsY on v126
(presses five frames apart; this time Xemnas NAMED PLAYER 2'S HERO): the lasers hit PLAYER 1'S hero (victim P1, made by the
script, counter 8586 ..), while all reflect pieces went onto player 2's hero; from 8920 to 10600 both heroes hung in hit
moves (each hit mirrored to the other), the reflects stopped after 10 and the dome failed (no success moves; the fight
went on with 0x101). Runs xsN / xsQ / xsX (player 1 named) show the same: the lasers aim at player 1's hero (the engine's
player), whoever the dome named.
NOW (only with --holdshared), the two routines of the second form are changed:
 hs_rc: while a pair of glue 65 lives (only the dome), a command of PLAYER 2'S HERO (the twin, when he is one of the pair)
   is sent in PLAYER 1'S HERO'S name. Player 1's own press goes as it is. So every reflect piece and every hit piece runs
   on player 1's hero, as on the one hero of the game; the mirror gives each move to player 2's hero; the count goes up
   once a press.
 ip_one: while that pair lives and PLAYER 2'S HERO is held, he is "not the player" of the boss's script (his pieces, if a
   laser hits him directly, never end the dome a second time). When he is free: the game's answer.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared7.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hs_rc: player 2's" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("""Its fourth part: the dome's pieces run on ONE hero, as in the game (runs xsN / xsQ: with both heroes carrying a piece of the
dome's script the end ran twice; xsS: a second end four steps late faulted at 0x001E2AC0): hs_rc sends a press of the
pair's other hero in the named hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press), and ip_one (script call 1,309) answers "not the player" for the other hero while he is held in the pair.
""", """Its fourth part: the dome's pieces run on ONE hero, PLAYER 1'S, the one its lasers aim at, as in the game (runs xsN / xsQ:
with both heroes carrying a piece of the dome's script the end ran twice; xsS: a second end four steps late faulted at
0x001E2AC0; xsY: pieces on the named player 2 while the lasers hit player 1 failed the dome): hs_rc sends a press of
player 2's hero in player 1's hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press), and ip_one (script call 1,309) answers "not the player" for player 2's hero while he is held in the pair.
""")

rep('''hs_rc:                            # from hp_rc: a command of the pair's OTHER hero is sent in the NAMED hero's name (a1 = the hero)
    lui t7,0x000E
    lw t1,0x7EA4(t7)              # the pair's other hero
    bne a1,t1,hs_rc2
    nop
    lw a1,0x7EA0(t7)              # the named hero: the boss's pieces of the dome run on him, as in the game
hs_rc2:
''', '''hs_rc:                            # from hp_rc: a command of PLAYER 2'S hero in the pair is sent in PLAYER 1'S hero's name (a1 = the hero)
    lui t7,0x000F
    lw t1,0x05CC(t7)              # the twin
    bne a1,t1,hs_rc2
    lui t7,0x0035
    lw a1,0x2400(t7)              # hs_rc: player 2's press goes in player 1's hero's name (the lasers aim at him; the pieces run on him)
hs_rc2:
''')

rep('''    lui t7,0x000E
    lw t1,0x7EA0(t7)              # a living pair (with --holdshared: the laser dome)
    beq t1,zero,ip_out
    lw t1,0x7EA4(t7)              # its other hero
    ld t0,16(sp)
    bne t0,t1,ip_out
    nop
''', '''    lui t7,0x000E
    lw t1,0x7EA0(t7)              # a living pair (with --holdshared: the laser dome)
    beq t1,zero,ip_out
    lui t1,0x000F
    lw t1,0x05CC(t1)              # player 2's hero (the twin)
    ld t0,16(sp)
    bne t0,t1,ip_out
    nop
''')
rep('''    sw zero,0(a0)                 # held in the pair: he is not "the player" of the boss's script (its pieces and its end stay with the named hero)
''', '''    sw zero,0(a0)                 # held in the pair: he is not "the player" of the boss's script (its pieces and its end stay with player 1's hero)
''')
rep('''            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not the pair's other hero while he is held")
''', '''            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not player 2's hero while he is held in the pair")
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
