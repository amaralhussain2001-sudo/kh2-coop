"""One-off: THE SEVENTY-THIRD GLUE of tools/merge/merge_v7.py (--itemtarget): A TARGET CHOICE FOR POTIONS, ETHERS AND ELIXIRS
(tenth round, the user's answer to the inspection proposals of 2026-11-15 night: "do 1 and 4", proposal 1).
BEFORE (lane N, docs/lanes/N-down-and-rescue.md section 3): the item target window "PARTY" has one row per party member (Sora,
Donald, Goofy); the second hero is no party member, both heroes are "Sora", and lane N's n_heal picks the hero by a rule (the
hero who is down, else the user). A standing hero could not give a Potion to a standing, hurt partner.
READ (research of 2026-11-16, all in the program): the PARTY list is list 4 of a menu's control object S (S + 0x1F4: + 8 count,
rows of 12 bytes, at most 8; + 0x6C the cursor row); 0x001BEC68 (called only at 0x001BE3A4, S's method 0x001BE358) rebuilds it on
every update from party members 0 .. 2 (0x00176B20) and keeps each row's object in S + 0xA5C[row] (3 words; S + 0xA68 belongs to
list 8). A row is added by 0x001BC780(list, command id, 0, 1); the command id of a character is 0x001B77E8(status id) (0x2A =
Sora). The confirmed row's object is read ONLY at 0x001BE2C4 (no other code reads S + 0xA5C) and passed to 0x00190878; the hero
then queues the item with the target's STATUS ID (entry + 0x10; + 0xC = the user's id, + 8 = the user's object); 0x001BA528
draws the effect on the member found by that id (0x00176B58 at 0x001BA53C) and 0x001BA598 applies it (lane N's n_heal at
0x001BA624). Potion, Hi-Potion, Ether and Elixir open this window; Mega-Potion / Mega-Ether / Megalixir (whole party) and the
shortcuts (the user himself) do not.
THE GLUE:
  ih_rows (0x001BE3A4, was jal 0x001BEC68): the game's rows, then, when the twin passes the builder's own three tests and has
    the same status id as player 1's hero, ONE MORE ROW for him (his name: "Sora" / "Roxas"). Its row number is kept for that
    menu (0x000E7FB0 player 1's menu, 0x000E7FB4 player 2's menu = S2 0x000F1000; -1 = none). On both screens the FIRST Sora
    is player 1's hero and the LAST Sora is player 2's hero.
  ih_row (0x001BE2BC .. 0x001BE2C4, was the read of S + 0xA5C[row]): the twin's row gives the twin as the target, every other
    row the game's member; the choice is noted for the menu's owner (S + 0x9E0) with the game's counter (player 1's hero:
    0x000E7FB8 / 0x000E7FBC; the twin: 0x000E7FC0 / 0x000E7FC4).
  ih_find (0x001BA53C, was jal 0x00176B58, only for a queued entry: 0x001BA528 called from 0x001BA484): the effect is drawn on
    the chosen hero.
  ih_pick (0x001BA624, was lane N's jal n_heal): a fresh choice (under 300 counts) of a HERO by the item's user, target = the
    heroes' id: player 1's hero -> the game's own routine 0x001A2A50 (his slot); the twin -> lane N's own step for the twin's
    slot (n_he_slot 0x000F2BB4, set up as n_heal does). The choice is used up. Everything else (shortcuts, helpers, a friend's
    row, party-wide items, no twin) goes to n_heal as before, with lane N's rule.
Code at 0x000EEA00 .. 0x000EEC00 (free, inside this round's room); values 0x000E7FB0 .. 0x000E7FC7 (free).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_itemtarget.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--itemtarget" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-THIRD GLUE (built only with the option --itemtarget): A TARGET CHOICE FOR POTIONS, ETHERS AND ELIXIRS. The item target
window "PARTY" gets one more row for the second hero (ih_rows at 0x001BE3A4): on both screens the first "Sora" is player 1's
hero and the last "Sora" player 2's. ih_row (0x001BE2BC) gives the chosen hero as the target and notes the choice for the menu's
owner; ih_find (0x001BA53C) draws the effect on him; ih_pick (0x001BA624, in front of lane N's n_heal) gives the item to the
chosen hero. Shortcuts, helpers and party-wide items keep lane N's rule.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- seventy-third glue (only with --itemtarget) ------------------------------------------------------------
II_AT = 0x000EEA00
II_END = 0x000EEC00
II_SRC = """
ih_rows:                          # from 0x001BE3A4 (was jal 0x001BEC68): a0 = s0 = the menu's control object S
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    jal 0x001BEC68                # the game's rows (party members 0 .. 2)
    move s0,a0
    lui t7,0x000F
    addiu t6,t7,0x1000            # S2 = player 2's control object
    lui t5,0x000E
    bne s0,t6,ir_v
    addiu t5,t5,0x7FB0            # player 1's menu: its twin row number
    addiu t5,t5,4                 # player 2's menu: 0x000E7FB4
ir_v:
    addiu t4,zero,-1
    sw t4,0(t5)                   # no twin row (yet)
    sd t5,16(sp)
    lw a0,0x05CC(t7)              # the twin (lane E; 0 = none)
    beq a0,zero,ir_out
    nop
    jal 0x0019BA60                # the builder's first test
    nop
    beq v0,zero,ir_out
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lw t4,0x588(t6)               # the builder's second test: no flag 0x400000
    lui t3,0x0040
    and t4,t4,t3
    bne t4,zero,ir_out
    nop
    lw t4,0x48C(t6)               # the third: a unit slot
    beq t4,zero,ir_out
    nop
    lw t4,8(t6)                   # the same status id as player 1's hero (both Sora, both Roxas)
    lhu t4,0x4C(t4)
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero (0x0034E948)
    beq t3,zero,ir_out
    nop
    lw t3,8(t3)
    lhu t3,0x4C(t3)
    bne t4,t3,ir_out
    nop
    lw t4,0x1FC(s0)               # the list's count = the new row's number
    sltiu t3,t4,8
    beq t3,zero,ir_out            # (at most 8 rows)
    ld t5,16(sp)
    sw t4,0(t5)                   # remembered for this menu
    lw a0,8(t6)
    jal 0x001B77E8                # the row's command (the character's name)
    lhu a0,0x4C(a0)
    move a1,v0
    addiu a0,s0,0x1F4             # list 4, PARTY
    move a2,zero
    jal 0x001BC780
    addiu a3,zero,1
ir_out:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32

ih_row:                           # from 0x001BE2BC (was: sll t7,t7,2 / addu t7,t7,s1 / lw a1,0xA5C(t7)): t7 = the confirmed
    lui t6,0x000F                 # row, s1 = S; out: a1 = the target. a0 / a2 and the s registers must stay
    addiu t5,t6,0x1000
    lui t4,0x000E
    bne s1,t5,irw_1
    addiu t4,t4,0x7FB0
    addiu t4,t4,4
irw_1:
    lw t3,0(t4)
    bne t7,t3,irw_game
    nop
    lw a1,0x05CC(t6)              # the twin's row: the twin
    b irw_note
    nop
irw_game:
    sll t3,t7,2                   # the game's row: its member
    addu t3,t3,s1
    lw a1,0xA5C(t3)
irw_note:
    lw t3,0x9E0(s1)               # the menu's owner (the hero who uses the item)
    lw t5,0x05CC(t6)
    lui t4,0x000E
    bne t3,t5,irw_2
    addiu t4,t4,0x7FB8            # player 1's hero: 0x000E7FB8 (object), 0x000E7FBC (counter)
    addiu t4,t4,8                 # the twin: 0x000E7FC0, 0x000E7FC4
irw_2:
    sw a1,0(t4)
    lui t3,0x0035
    lw t3,-11076(t3)              # the game's counter (0x0034D4BC)
    jr ra
    sw t3,4(t4)

ih_find:                          # from 0x001BA53C in 0x001BA528 (the effect of a queued item is drawn on the member whose id is a0)
    lw t7,16(sp)                  # 0x001BA528's caller: 0x001BA48C = one queued entry, then s0 = the entry
    lui t6,0x001B
    ori t6,t6,0xA48C
    bne t7,t6,if_game
    lui t6,0x000F
    lw t5,0x05CC(t6)              # the twin
    beq t5,zero,if_game
    lw t4,8(s0)                   # the user
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero
    lui t2,0x000E
    beq t4,t3,if_v
    addiu t2,t2,0x7FB8
    bne t4,t5,if_game
    nop
    addiu t2,t2,8
if_v:
    lw t1,0(t2)                   # the chosen hero (not used up here)
    beq t1,t5,if_hero
    nop
    bne t1,t3,if_game
    nop
if_hero:
    lw t0,8(t5)
    lhu t0,0x4C(t0)
    bne a0,t0,if_game             # the target is the heroes' id
    lui t0,0x0035
    lw t0,-11076(t0)
    lw t7,4(t2)
    subu t0,t0,t7
    sltiu t0,t0,300
    beq t0,zero,if_game
    nop
    jr ra
    move v0,t1
if_game:
    j 0x00176B58
    nop

ih_pick:                          # from 0x001BA624 (was lane N's jal n_heal): a0 effect, a1 target id, a2 user id, a3 boost,
    lui t6,0x000F                 # s1 = the queued entry (+ 8 = the user's object)
    lw t5,0x05CC(t6)              # the twin
    beq t5,zero,ip_old
    lw t4,8(s1)                   # the user
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero
    lui t2,0x000E
    beq t4,t3,ip_v
    addiu t2,t2,0x7FB8
    bne t4,t5,ip_old
    nop
    addiu t2,t2,8
ip_v:
    lw t1,0(t2)                   # the chosen object (0 = none)
    beq t1,zero,ip_old
    sw zero,0(t2)                 # used up
    lui t0,0x0035
    lw t0,-11076(t0)
    lw t7,4(t2)
    subu t0,t0,t7
    sltiu t0,t0,300
    beq t0,zero,ip_old            # too old: lane N's rule
    nop
    lw t0,8(t5)
    lhu t0,0x4C(t0)               # the heroes' status id
    bne a1,t0,ip_old              # a friend is the target: lane N's rule (the game's routine)
    nop
    beq t1,t3,ip_hero
    nop
    bne t1,t5,ip_old
    nop
    addiu sp,sp,-64               # the twin: lane N's own step for his slot, set up as n_heal does it
    sd ra,0(sp)
    sd s0,8(sp)
    sd s2,16(sp)
    sd s3,24(sp)
    sd s4,32(sp)
    sd s5,40(sp)
    move s0,a0
    move s2,a1
    move s3,a2
    move s4,a3
    jal 0x000F2BB4                # n_he_slot
    move s5,t5
    ld ra,0(sp)
    ld s0,8(sp)
    ld s2,16(sp)
    ld s3,24(sp)
    ld s4,32(sp)
    ld s5,40(sp)
    addiu sp,sp,64
    jr ra
    move v0,zero
ip_hero:
    j 0x001A2A50                  # player 1's hero: the game's own routine (the heroes' id = his slot)
    nop
ip_old:
    j 0x000F2A9C                  # lane N's n_heal
    nop
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--itemtarget" in sys.argv:                                         # seventy-third glue (a target choice for single items)
        assert words.get(0x001BA624) == 0x0C03CAA7, "lane N's n_heal call is not at 0x001BA624"
        assert words.get(0x000F2A9C) == 0x3C0F000F and words.get(0x000F2BB4) == 0x27BDFFF0, "lane N's n_heal / n_he_slot moved"
        labels, n = add_code(II_AT, II_END, II_SRC, {}, "a target choice for Potions, Ethers and Elixirs")
        hook_game(0x001BE3A4, 0x0C06FB1A, jal(labels["ih_rows"]), "the PARTY rows: one more for the second hero")
        hook_game(0x001BE2BC, 0x000F7880, jal(labels["ih_row"]), "a PARTY row is confirmed: the second hero's row gives him")
        hook_game(0x001BE2C0, 0x01F17821, 0x00000000, "(the rest of the game's read of the row's member, now in ih_row)")
        hook_game(0x001BE2C4, 0x8DE50A5C, 0x00000000, "(the rest of the game's read of the row's member, now in ih_row)")
        hook_game(0x001BA53C, 0x0C05DAD6, jal(labels["ih_find"]), "a queued item's effect: drawn on the chosen hero")
        hook_base(0x001BA624, 0x0C03CAA7, jal(labels["ih_pick"]), "a queued item takes effect: on the chosen hero, else lane N's rule")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
