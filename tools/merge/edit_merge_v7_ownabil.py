"""One-off: tools/merge/merge_v7.py gets the FIFTY-EIGHTH GLUE (built only with --ownabil; AN EXPERIMENT for plan
row 39, stage 1b): PLAYER 2 SWITCHES HIS OWN ABILITIES ON AND OFF.
What was read (eighth round, part 79):
- A record's ability list is 80 shorts at record + 0x54; 0x8000 = switched on; every reader masks the number with
  0x7FFF (14 places). A new ability goes into THE FIRST EMPTY PLACE (the adder 0x00188B68(record, number, on);
  callers 0x0016E738, 0x001A3284): the list only grows, a place keeps its ability. So "player 2's switch of
  place i" can be one bit per place.
- A hero's abilities are read through HIS slot's record at the moment they matter (runs e1b / e1c, part 13); the
  twin's slot reads the view T (glue 48).
The design (the same as for his armour and accessories, glues 48 / 49):
- PLAYER 2'S EIGHTY SWITCHES are five shorts in the save data (P2A), a mark behind them (P2A + 10 = 0x5032).
  Where: King Mickey's record (the fourth of the thirteen, 0x0032E35C), its item places + 0x34 .. + 0x3F. HYPOTHESIS
  until a dump shows that his count of item places (+ 0x12) is 0 in every state of the game: then nothing reads
  them, and they are saved and loaded with the game's own save.
- ab_init: no mark yet (a New Game, an old save): his switches are made = the hero's.
- ab_view (glue 48's hero path, was "sw t3,0x30(t6)"): the view T gets his switches in place of the hero's.
- ab_swap (the end of glue 49's ow_swap): while player 2's pause menu is open the hero's switches and his change
  places in the hero's record, so the game's own Abilities menu shows and edits his.
- ab_add (the jump at 0x00188B90, the adder's store): an ability given to the hero is given to player 2 with the
  same switch (on when the game gives it switched on).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownabil.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "ab_view" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-EIGHTH GLUE (built only with the option --ownabil, with --ownrec --ownmenu; an experiment): PLAYER 2
SWITCHES HIS OWN ABILITIES. The ability list (80 shorts at record + 0x54, 0x8000 = on) only grows (the adder
0x00188B68 takes the first empty place), so his switches are one bit per place: five shorts at P2A (King
Mickey's record, item places; a mark 0x5032 behind them). ab_init makes them from the hero's when the mark is
not there; ab_view puts them into the view T; ab_swap changes them with the hero's while player 2's pause menu
is open; ab_add gives him each new ability with the switch the game gives it.

'''
s = s.replace(a, hdr + a)
b = " [--hudowner]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--ownabil]")

i = s.index("def main():")
src = '''# ---- fifty-eighth glue, an experiment (only with --ownabil) -------------------------------------------------
GA_AT = 0x000EBD00
GA_END = 0x000EBF00
P2A = 0x0032E390                                   # player 2's eighty ability switches (five shorts), the mark at + 10
P2A_LO = P2A - 0x00330000                          # (as an offset from lui 0x0033)
GA_SRC = """
ab_init:                          # in: t9 = the hero's record. No mark: player 2's switches are made = the hero's
    lui t8,0x0033
    lhu t0,@MARK@(t8)
    addiu t1,zero,0x5032
    beq t0,t1,ai_out
    addiu t2,t9,0x54              # the list
    addiu t8,t8,@BITS@
    addiu t3,zero,5
ai_w:
    move t0,zero
    addiu t1,zero,16
ai_b:
    lhu t4,0(t2)
    srl t0,t0,1
    andi t4,t4,0x8000
    or t0,t0,t4                   # the first place of the sixteen ends in bit 0
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,ai_b
    nop
    sh t0,0(t8)
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,ai_w
    nop
    addiu t1,zero,0x5032
    sh t1,0(t8)                   # the mark
ai_out:
    jr ra
    nop

ab_view:                          # jump in glue 48's hero path (was sw t3,0x30(t6); its delay slot: sw t6,0x244(a0)). t6 = T, a1 = the hero's record
    sw t3,0x30(t6)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal ab_init
    move t9,a1
    lui t8,0x0033
    addiu t8,t8,@BITS@
    addiu t2,t6,0x54              # T's list
    addiu t3,zero,5
av_w:
    lhu t0,0(t8)                  # sixteen switches of player 2's, the first place in bit 0
    addiu t1,zero,16
av_b:
    lhu t4,0(t2)
    andi t4,t4,0x7FFF
    beq t4,zero,av_n              # an empty place stays empty
    andi t5,t0,1
    sll t5,t5,15
    or t4,t4,t5
av_n:
    sh t4,0(t2)
    srl t0,t0,1
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,av_b
    nop
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,av_w
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    j 0x001A1214                  # the end of glue 48's tl_use
    daddu s1,t6,zero

ab_swap:                          # from the end of glue 49's ow_swap (was jr ra): the hero's switches and player 2's change places
    lui t5,0x000E
    lw t9,0x7E28(t5)              # the hero's record
    beq t9,zero,as_out
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal ab_init
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    lui t8,0x0033
    addiu t8,t8,@BITS@
    addiu t2,t9,0x54
    addiu t3,zero,5
aw_w:
    lhu t0,0(t8)
    move t5,zero
    addiu t1,zero,16
aw_b:
    lhu t4,0(t2)
    srl t5,t5,1
    andi t6,t4,0x8000
    or t5,t5,t6                   # the hero's switch, collected
    andi t4,t4,0x7FFF
    beq t4,zero,aw_n              # an empty place has no switch
    andi t6,t0,1
    sll t6,t6,15
    or t4,t4,t6
aw_n:
    sh t4,0(t2)
    srl t0,t0,1
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,aw_b
    nop
    sh t5,0(t8)
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,aw_w
    nop
as_out:
    jr ra
    nop

ab_add:                           # jump at 0x00188B90 (was or t7,t5,a1 [now its delay slot] / jr ra / sh t7,4(a0)). t6 = the place, a1 = on << 15
    sh t7,4(a0)
    sll t0,t6,1
    subu t0,a0,t0
    addiu t0,t0,-0x50             # the record the ability went into
    lui t5,0x000E
    lw t1,0x7E28(t5)              # the hero's record
    bne t0,t1,aa_out
    lw t2,0x7E24(t5)              # (player 2's menu is open: the list holds his switches; nothing is given then)
    bne t2,zero,aa_out
    lui t8,0x0033
    lhu t1,@MARK@(t8)
    addiu t2,zero,0x5032
    bne t1,t2,aa_out              # his switches are not made yet: they will be made from the hero's
    srl t3,t6,4                   # which of the five shorts
    sll t3,t3,1
    addu t8,t8,t3
    lhu t0,@BITS@(t8)
    andi t4,t6,15
    addiu t1,zero,1
aa_m:
    beq t4,zero,aa_m2
    nop
    sll t1,t1,1
    b aa_m
    addiu t4,t4,-1
aa_m2:
    nor t2,t1,zero
    and t0,t0,t2
    beq a1,zero,aa_st
    nop
    or t0,t0,t1
aa_st:
    sh t0,@BITS@(t8)
aa_out:
    jr ra
    nop
""".replace("@MARK@", str(P2A_LO + 10)).replace("@BITS@", str(P2A_LO))


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--ownabil" in sys.argv:                                            # fifty-eighth glue, an experiment (player 2's own ability switches)
        assert "--ownrec" in sys.argv and "--ownmenu" in sys.argv, "--ownabil needs --ownrec --ownmenu"
        labels, n = add_code(GA_AT, GA_END, GA_SRC, {}, "EXPERIMENT: player 2 switches his own abilities")
        at = [x for x in range(RT_AT, RT_END, 4) if words.get(x) == 0xADCB0030]           # sw t3,0x30(t6): the last store of glue 48's hero path
        assert len(at) == 1, at
        hook_base(at[0], 0xADCB0030, (2 << 26) | ((labels["ab_view"] >> 2) & 0x3FFFFFF), "the view T is made: player 2's ability switches go in")
        at = [x for x in range(RM_AT, RM_END, 4) if words.get(x) == 0x03E00008]           # the first jr ra of glue 49: the end of ow_swap
        hook_base(min(at), 0x03E00008, (2 << 26) | ((labels["ab_swap"] >> 2) & 0x3FFFFFF), "player 2's menu opens or goes: the ability switches change places too")
        hook_game(0x00188B90, 0x01A57825, (2 << 26) | ((labels["ab_add"] >> 2) & 0x3FFFFFF), "a new ability goes into a record's list: player 2 gets its switch too")
        hook_game(0x00188B94, 0x03E00008, 0x01A57825, "(or t7,t5,a1 moved into the delay slot)")
        n_glue += n + 2

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
