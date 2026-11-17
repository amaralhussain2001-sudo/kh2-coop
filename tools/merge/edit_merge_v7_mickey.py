"""One-off: tools/merge/merge_v7.py gets the THIRTY-SEVENTH GLUE (King Mickey's rescue for two, plan row 45).
The record of the edit; run once:  python -I tools/merge/edit_merge_v7_mickey.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "mk_both" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''THIRTY-SEVENTH GLUE (option --no-mickey leaves it out; --mickey1 keeps only its last part): KING MICKEY'S RESCUE
FOR TWO (plan row 45, register F1).
What was there: when both heroes are down in one of the eleven Mickey missions and the roll is won, the game parks
the engine's player (0x00179E48: the hero goes from 0x0034E948 to the parking place 0x0034E94C), builds King
Mickey as a NEW player object with the fallen hero's controller (0x001D00A8) and holds the hero in Mickey's paired
move 252. Player 1 plays Mickey; player 2 watches his fallen hero. The rescue ends in 0x001D0228 (paired move 253)
or 0x001D02C8 (move 254, Mickey's "Healing Light", effect kind 4): Mickey's end method, the parked hero back
(0x00179EB8), the paired move that lifts him. The twin stayed down for the rest of the fight.
Now:
(1) mk_both (the call at 0x001AF628): after the game's call, when the twin is down too, the same routine runs a
    second time with the twin as "the player": he is parked (in the glue's own place 0x000E7C00), a second Mickey
    is built with HIS controller and holds him in move 252. That Mickey is "the twin" (0x000F05CC) for the length
    of the rescue, so player 2's view, HUD, menu and controller are his. The engine's player and the game's attach
    go back to player 1's Mickey.
(2) mk_end (the two calls of the end routines, 0x00172EBC and 0x001BA5C8): whichever Mickey ends the rescue, both
    end: the game's routine for player 1's Mickey, then the same routine for the second Mickey with the twin in
    the parking place; the twin is the twin again, the engine's player is player 1's hero again.
(3) a twin who is still down after the rescue's end is brought back the way lane N brings a hero back (his class's
    HP change with lane N's "down" word set), and his HP is filled as the hero's is. With --mickey1 only this part
    is built (one Mickey, played by player 1; the Healing Light brings both heroes back).

'''
s = s.replace(a, hdr + a)
b = "[--no-formfiles] [--no-nearcb]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-mickey | --mickey1]")
i = s.index("def main():")
src = '''# ---- thirty-seventh glue -----------------------------------------------------------------------------------
MK_AT = 0x000E8600
MK_END = 0x000E8800
V_PARK2 = 0x000E7C00                               # the twin's fallen hero while a second Mickey plays (0 = none)
MK_SRC = """
mk_both:                          # from 0x001AF628 (was jal 0x001D00A8): the Game Over sequence builds King Mickey
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    jal 0x001D00A8                # the game's call: Mickey for the engine's player
    nop
@TWO@
mb_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
mk_end253:                        # from 0x00172EBC (was j 0x001D0228). a0 = the Mickey that ends
    lui t9,0x001D
    b mk_end
    ori t9,t9,0x0228
mk_end254:                        # from 0x001BA5C8 (was jal 0x001D02C8)
    lui t9,0x001D
    ori t9,t9,0x02C8
mk_end:
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s3,t9                    # the game's end routine
    move s0,a0
    lui t7,0x000E
    lw s1,0x7C00(t7)              # the parked twin (0 = there is no second Mickey)
    beq s1,zero,me_one
    lui t6,0x000F
    lw s2,0x05CC(t6)              # the second Mickey
    lui t5,0x0035
    lw a0,-5816(t5)               # player 1's Mickey = the engine's player
    jalr s3                       # the game's routine: he ends, player 1's hero is back
    nop
    lui t5,0x0035
    lw t4,-5816(t5)               # player 1's hero
    sd t4,40(sp)
    sw s2,-5816(t5)               # "the player" = the second Mickey
    sw s1,-5812(t5)               # the parked hero = the twin
    jalr s3                       # the same routine: he ends, the twin is back
    move a0,s2
    lui t6,0x000F
    sw s1,0x05CC(t6)              # the twin is the twin again
    lui t7,0x000E
    sw zero,0x7C00(t7)
    ld a0,40(sp)
    lui t5,0x0035
    sw a0,-5816(t5)               # the engine's player = player 1's hero
    sw zero,-5812(t5)
    sw a0,0x2400(t5)              # 0x00352400: the last-built object of the main player class
    jal 0x001781A8                # the game's attach for player 1's hero (camera target, HUD owner, control object)
    nop
    b me_fill
    nop
me_one:
    jalr s3                       # one Mickey: the game's routine as it is
    move a0,s0
me_fill:                          # a twin who is still down gets up; his HP is filled as the hero's is
    lui t6,0x000F
    lw s1,0x05CC(t6)
    beq s1,zero,me_out
    nop
    lw t3,0x48C(s1)               # his unit slot
    beq t3,zero,me_out
    nop
    lw t5,0x7F8(s1)
    andi t5,t5,4
    beq t5,zero,me_hp             # he is up
    nop
    li t4,1
    sw t4,0x2FCC(t6)              # lane N's word "the twin is down by my rule": a heal brings him back
    lw a1,4(t3)                   # most HP
    move a0,s1
    move a2,zero
    move a3,zero
    lw t7,0(s1)
    lw t7,0x78(t7)
    jalr t7                       # his class's HP change (lane N's n_hp)
    nop
me_hp:
    lw t3,0x48C(s1)
    beq t3,zero,me_out
    nop
    lw t4,4(t3)
    sw t4,0(t3)                   # full HP
me_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,64
"""
MK_TWO = """
    lui t7,0x000F
    lw s0,0x05CC(t7)              # the twin
    beq s0,zero,mb_out
    nop
    lw t6,0x7F8(s0)
    andi t6,t6,4
    beq t6,zero,mb_out            # he is not down: nothing more
    lui t5,0x0035
    lw s1,-5816(t5)               # player 1's Mickey (the engine's player now)
    lw s2,-5812(t5)               # player 1's parked hero
    beq s1,zero,mb_out
    nop
    beq s2,zero,mb_out            # no Mickey was built
    nop
    sw s0,-5816(t5)               # "the player" = the twin
    sw zero,-5812(t5)
    jal 0x001D00A8                # the same routine: the twin is parked, a Mickey with his controller holds him
    nop
    lui t5,0x0035
    lw t4,-5816(t5)               # the second Mickey
    lw t3,-5812(t5)               # the parked twin
    lui t7,0x000E
    sw t3,0x7C00(t7)
    lui t7,0x000F
    sw t4,0x05CC(t7)              # the second Mickey is "the twin" for the length of the rescue
    sw s1,-5816(t5)               # the engine's player = player 1's Mickey
    sw s2,-5812(t5)               # the parking place = player 1's hero
    jal 0x001781A8                # the game's attach for player 1's Mickey
    move a0,s1
"""
MK_HOOKS = (
    (0x001AF628, 0x0C07402A, "jal", "mk_both", "the Game Over sequence builds King Mickey: one for each fallen hero"),
    (0x00172EBC, 0x0807408A, "j", "mk_end253", "the rescue ends (paired move 253): both Mickeys end, both heroes are back"),
    (0x001BA5C8, 0x0C0740B2, "jal", "mk_end254", "the rescue ends (Healing Light): both Mickeys end, both heroes are back"),
)


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-mickey" not in sys.argv:                                      # thirty-seventh glue
        src = MK_SRC.replace("@TWO@", "" if "--mickey1" in sys.argv else MK_TWO)
        labels, n = add_code(MK_AT, MK_END, src, {}, "King Mickey's rescue for two")
        for a, w0, kind, label, what in MK_HOOKS:
            hook_game(a, w0, ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF), what)
        n_glue += n + len(MK_HOOKS)

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
