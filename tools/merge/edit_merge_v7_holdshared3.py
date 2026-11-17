"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, SECOND PART (option --holdshared): THE SHARED MECHANIC'S COMMAND IS IN BOTH
HEROES' MENUS (ninth round, the user's items 1 and 4 of 2026-11-15 evening: "both players should participate meaningfully";
STATE part 110).
SEEN (runs xsD / xsE / xsG on candidate v122, the last Xemnas's laser dome, ONLY PLAYER 2 pressing): player 2's presses
never reach the forty-seventh glue's rc_one (recorder tools/own/make_rec_rc.py: 0 calls in the dome, 32 after it); all
935 offers of command 650 "Reflect" go to PLAYER 1'S control object (recorder tools/own/make_rec_offer2.py: return
address 0x00174378, the engine's player = player 1's hero). READ: the dome's "Reflect" is offered each step by a thread
of the boss's script (B_EX170_LAST, routine 16062: trap_command_override 650 / 651) through the script call (1,165)
0x00174328, which offers to *(the engine's player + 0xB44): player 1's menu only. (Shan-Yu's "Press" comes from the
script hooked onto each hero; the forty-third glue makes the twin "the player" there. The dome has no such piece.)
NOW (only with --holdshared): co_two takes the table word of the script call 165 (0x0034E228): the game's offer first;
then, while a pair of the sixty-fifth glue lives (0x000E7EA0 / A4; with --holdshared only the laser dome makes one) and
the engine's player is one of its two heroes, the OTHER hero is "the player" for one more offer: his own menu gets the
same command. His press then reaches rc_one with the captor as the source, and hp_rc lets it through (once a step).
Room: the sixty-eighth glue's range 0x000EE4C0 .. 0x000EE6C0 (--holdpads and --holdshared never go together).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "co_two" in s:
    raise SystemExit("already there")

a = """bystander is still not made, and the nets stay.
"""
assert s.count(a) == 1
s = s.replace(a, a + """Its second part: while that pair lives, a command the game offers to one hero of the pair (the script call 165, "command
override": the dome's "Reflect") is offered to the other hero's own menu too (co_two, in the sixty-eighth glue's room), so
each player's own press counts (once a step, the forty-seventh glue's hp_rc).
""")

a = "HP_TRAPS = ("
assert s.count(a) == 1
s = s.replace(a, '''CO_AT = 0x000EE4C0                                 # (--holdshared) co_two, in the sixty-eighth glue's room (never with --holdpads)
CO_END = 0x000EE6C0
CO_SRC = """
co_two:                           # the script call (1,165) "command override" (was 0x00174328). a0 = its inputs
    addiu sp,sp,-32
    sd ra,0(sp)
    jal 0x00174328                # the game's offer: to the engine's player's menu
    sd a0,8(sp)
    lui t7,0x000E
    lw t0,0x7EA0(t7)              # a living pair of the sixty-fifth glue (with --holdshared: only the laser dome)
    beq t0,zero,co_out
    lw t1,0x7EA4(t7)
    beq t1,zero,co_out
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq t4,t0,co_oth
    move t2,t1
    bne t4,t1,co_out
    move t2,t0
co_oth:
    sd t4,16(sp)
    sw t2,-5816(t5)               # the other hero of the pair is "the player" for one more offer: his own menu gets it too
    jal 0x00174328
    ld a0,8(sp)
    lui t5,0x0035
    ld t4,16(sp)
    sw t4,-5816(t5)
co_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""
''' + a)

a = "        n_glue += n + 1 + len(HP_TRAPS)\n"
assert s.count(a) == 1
s = s.replace(a, a + """        if "--holdshared" in sys.argv:                                     # (the fifth form's second part: the shared mechanic's command in both menus)
            labels, n = add_code(CO_AT, CO_END, CO_SRC, {}, "a command offered to one hero of a hold's pair goes to the other hero's menu too")
            hook_game(0x0034E228, 0x00174328, labels["co_two"], "the script call (1,165) 'command override': both heroes of a hold's pair")
            n_glue += n + 1
""")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
