"""One-off: tools/merge/merge_v7.py gets the SIXTY-THIRD GLUE (built only with --ownkey, with --ownitems and the
thirty-third glue): PLAYER 2'S OWN KEYBLADE (plan row 39, the rest; ninth round, part 91).

Read in the program:
 - a body's weapon item comes from 0x0016F610(object entry, hand): for Sora / Roxas the hero record's + 0 (hand 0)
   or + 2, or a Drive Form record's weapon (hand 1 of a form). It is asked when a body's FILES are asked for
   (0x0016EB48, the loop at 0x0016ECA8: weapon files get the body's number + 1 + hand: 2301, 2302) and when a
   player object is BUILT (0x00177DC8 inside the player factory 0x00179FD0).
 - the file pool lays the files out in the order of their numbers; the numbers 2300 .. 2399 have a block of
   their own whose size comes from the party table (0x001A89F0 -> 0x0016FAB0); inside a block a file that grows
   moves the files behind it (0x0016FC10 moves the data; the objects that use it are NOT told).
 - a weapon object finds its files BY NAME (0x00185468: the model through the object entry, the motion file
   through 0x001708F8(name, -1)). Every Keyblade has its own model and effect file (at most 252 KB together)
   and shares the motion file W_EX010.mset.
 - the menu changes a weapon with 0x00175F68 (glue 33's wc_both sits in front of it).
What the glue does. His Keyblade is a short in King Mickey's record (0x0032E35C + 0x40; + 0x42 = player 1's
Keyblade as last seen, + 0x46 = the mark 0x5034).
 kb_tick   (0x00138538) no mark: his Keyblade = player 1's. And when player 1's Keyblade is another one than last
           seen WITHOUT his menu having changed it (the story did), player 2 gets the same.
 kb_swap   (the end of oi_swap) while player 2's pause menu is open HIS Keyblade stands in the hero's record.
 kb_tview  (the end of oi_tview) the twin's view T has HIS Keyblade: his strength, magic, the Keyblade's ability.
 kb_fact   (lane E's call of the player factory, 0x000F0344) notes "a player object is being built".
 kb_rec    (0x0016F680) while the TWIN is being built, the first hand's weapon item is HIS Keyblade, if its files
           are there (a loaded file with the number 2303); else player 1's, whose files always are.
 kb_req    (0x0016ECDC) when the hero's normal body asks for its first weapon's files (number 2301) and player
           2's Keyblade is another one, its files are asked for too, with the number 2303 (the same block).
 kb_size   (0x001A8B20) the hero's block is 256 KB bigger, so a second Keyblade's model never pushes the files
           behind the block.
 kc_menu   (0x002933D0, in front of wc_both) the first hand of the hero's character: PLAYER 1's MENU: the twin's
           weapon is ended, the game's routine changes player 1's (kc_load, at its "load now" 0x0017607C, asks
           for player 2's files again or lets them go when both hold the same Keyblade now), the twin's weapon
           is built again with HIS Keyblade. PLAYER 2's MENU: only the twin's weapon is ended, his old files go
           (0x001703A8(2303)), the new ones are asked for (not when it is player 1's Keyblade), loaded, and his
           weapon is built; player 1's hero is not touched.
A Drive Form's second Keyblade stays common (the form's record).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "kb_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTY-THIRD GLUE (built only with the option --ownkey, with --ownitems): PLAYER 2'S OWN KEYBLADE (plan row 39).
His Keyblade is a short in King Mickey's record (0x0032E35C + 0x40; + 0x42 player 1's as last seen; + 0x46 the
mark 0x5034). kb_tick makes it and lets it follow a change the STORY makes; kb_swap puts it into the hero's
record while his pause menu is open; kb_tview gives the twin's view his Keyblade (his stats); kb_fact / kb_rec
(0x000F0344, 0x0016F680): while the twin is built his first hand gets HIS Keyblade when its files are there;
kb_req (0x0016ECDC): its files are asked for with the number 2303, in the hero's own block of the file pool;
kb_size (0x001A8B20): that block is 256 KB bigger; kc_menu / kc_load (0x002933D0, 0x0017607C): a Keyblade change
in player 1's menu rebuilds the twin's weapon with HIS Keyblade, a change in player 2's menu changes the twin's
weapon and files only.

'''
s = s.replace(a, hdr + a)
b = " [--ownitems]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--ownkey]")

i = s.index("def main():")
src = '''# ---- sixty-third glue (only with --ownkey) ------------------------------------------------------------------
KB_AT = 0x000EC700
KB_END = 0x000ECD00
P2KB = P2B + 0x40 - 0x00330000                     # player 2's Keyblade (a short)
P2LW = P2B + 0x42 - 0x00330000                     # player 1's Keyblade as last seen
P2KM = P2B + 0x46 - 0x00330000                     # 0x5034 = his Keyblade is made
KB_SRC = """
kb_tick:                          # from 0x00138538 (each step the field looks for START)
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,kt_go             # player 2's menu is open (cannot be: the field does not look then)
    lui t8,0x0033
    lhu t2,-8160(t8)              # player 1's Keyblade now (Sora's record + 0)
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    beq t0,t1,kt_have
    lhu t3,@LW@(t8)
    sh t2,@KB@(t8)                # no mark: player 2's Keyblade is made = player 1's
    sh t2,@LW@(t8)
    b kt_go
    sh t1,@KM@(t8)
kt_have:
    beq t2,t3,kt_go
    nop
    sh t2,@LW@(t8)                # the story gave player 1 another Keyblade: player 2 gets the same
    sh t2,@KB@(t8)
kt_go:
    j TICK_NEXT
    move a0,zero

kb_swap:                          # jump at the end of glue 62's oi_swap (was jr ra): player 2's menu opens or goes
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record
    beq t9,zero,kw_out
    lui t8,0x0033
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    beq t0,t1,kw_do
    lhu t2,0(t9)
    sh t2,@KB@(t8)                # (no mark yet: his Keyblade is made = player 1's, first)
    sh t2,@LW@(t8)
    sh t1,@KM@(t8)
kw_do:
    lhu t3,@KB@(t8)
    sh t3,0(t9)
    sh t2,@KB@(t8)
kw_out:
    jr ra
    nop

kb_tview:                         # jump at the end of glue 62's oi_tview (was j 0x001A1214): the hero's view T is made
    lui t8,0x0033
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    bne t0,t1,kv_go
    lui t9,0x000E
    lhu t0,@KB@(t8)
    beq t0,zero,kv_go
    nop
    sh t0,0x7D00(t9)              # the view's Keyblade is player 2's: his strength, his magic, the Keyblade's ability
kv_go:
    j 0x001A1214
    nop

kb_fact:                          # call at 0x000F0344 (lane E's e_wrap; was jal 0x00179FD0, the player factory)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    addiu t6,zero,1
    jal 0x00179FD0
    sw t6,0x7E88(t7)              # a player object is being built
    lui t7,0x000E
    sw zero,0x7E88(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

kb_rec:                           # call at 0x0016F680 (was jal 0x00188FE0: the record of a character). a1 = the character number, s0 = the hand
    lui t7,0x000E
    lw t6,0x7E88(t7)
    beq t6,zero,kr_game           # no player object is being built: the game's way (file requests too)
    lui t6,0x000F
    lw t6,0x05C4(t6)              # lane E: is it player 1's hero
    bne t6,zero,kr_game
    nop
    bne s0,zero,kr_game           # the second hand: common
    addiu t6,zero,1
    beq a1,t6,kr_hero
    addiu t6,zero,14
    bne a1,t6,kr_game
    nop
kr_hero:
    lw t6,0x7E24(t7)
    bne t6,zero,kr_game           # (player 2's menu is open: the record holds his Keyblade already)
    lui t8,0x0033
    lhu t6,@KM@(t8)
    addiu t5,zero,0x5034
    bne t6,t5,kr_game
    lhu t6,@KB@(t8)
    beq t6,zero,kr_game
    lhu t5,-8160(t8)
    beq t6,t5,kr_game             # the same Keyblade as player 1's: the same files
    lui t4,0x0035
    lw t4,-9056(t4)               # the file pool's list: is a file of his Keyblade (number 2303) loaded
kr_w:
    beq t4,zero,kr_game           # no: player 1's Keyblade, whose files are there
    nop
    lw t3,0x28(t4)
    addiu t2,zero,2303
    bne t3,t2,kr_n
    lbu t3,1(t4)
    addiu t2,zero,3
    beq t3,t2,kr_own
    nop
kr_n:
    b kr_w
    lw t4,0x3C(t4)
kr_own:
    jr ra
    addiu v0,t8,@KB@              # "his record": the routine reads the first hand's weapon at + 0
kr_game:
    j 0x00188FE0
    nop

kb_req:                           # call at 0x0016ECDC (was jal 0x0016EF58: ask for a weapon's files). a0 = the weapon set, a1 = the hand, a3 = the number, s5 = the body's entry, s6 = a flag bit
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a3,24(sp)
    sd t0,32(sp)
    jal 0x0016EF58                # the game's request (player 1's Keyblade)
    nop
    ld a1,16(sp)
    bne a1,zero,kq_out            # the second hand
    ld a3,24(sp)
    addiu t6,zero,2301
    bne a3,t6,kq_out              # not the hero's normal body (a form finds the model by its name)
    lhu t6,76(s5)                 # whose body
    addiu t5,zero,1
    beq t6,t5,kq_hero
    addiu t5,zero,14
    bne t6,t5,kq_out
    nop
kq_hero:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kq_out
    lui t8,0x0033
    lhu t6,@KM@(t8)
    addiu t5,zero,0x5034
    bne t6,t5,kq_out
    lhu a1,@KB@(t8)
    beq a1,zero,kq_out
    lhu t5,-8160(t8)
    beq a1,t5,kq_out              # the same Keyblade as player 1's: one set of files
    nop
    jal 0x00185890                # the weapon object of this body's set for player 2's Keyblade
    ld a0,8(sp)
    beq v0,zero,kq_out
    or a2,v0,s6
    ld a0,8(sp)
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58
    ld t0,32(sp)
kq_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48

kb_size:                          # jump at 0x001A8B20 (was j 0x0016FAB0: the sizes of the hero's and the helpers' blocks). a0 = the hero's
    beq a0,zero,kz_go
    lui t7,0x0004
    addu a0,a0,t7                 # room for a second Keyblade's model and effect file (252 KB at most)
kz_go:
    j 0x0016FAB0
    nop

kc_set:                           # out: v0 = the weapon set of the twin's body for the first hand (s0 = the twin)
    lw t6,8(s0)
    lhu v0,78(t6)
    addiu t7,zero,53
    beq v0,t7,ks_out
    nop
    lw t7,0x588(s0)
    lui t6,0x0100
    and t7,t7,t6
    beq t7,zero,ks_out
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001D1438                # (the game's own detour for the first hand of a form body: the base body's weapon set)
    move a0,zero
    jal 0x0016E920
    move a0,v0
    lhu v0,78(v0)
    ld ra,0(sp)
    addiu sp,sp,16
ks_out:
    jr ra
    nop

kc_menu:                          # jump at 0x002933D0 (was j wc_both). a0 = the menu's record, a1 = the character number, a2 = the hand, a3 = the new weapon item
    bne a2,zero,kc_old            # the second hand: as before (glue 33)
    lui t8,0x0033
    lhu t5,@KM@(t8)
    addiu t4,zero,0x5034
    bne t5,t4,kc_old
    addiu t4,zero,1
    beq a1,t4,kc_h
    addiu t4,zero,14
    bne a1,t4,kc_old              # another character's weapon: as before
    nop
kc_h:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kc_h2
    nop
    sh a3,@LW@(t8)                # player 1's own change of his Keyblade (not the story's)
kc_h2:
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,kc_old
    nop
    addiu sp,sp,-96
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    sd s4,40(sp)
    sd s5,48(sp)
    move s0,t6
    move s1,a0
    move s2,a1
    move s3,a3
    jal 0x0016A070                # the twin's character number
    move a0,s0
    beq v0,s2,kc_mine
    nop
    move a0,s1                    # the twin is another character (King Mickey): as before
    move a1,s2
    move a2,zero
    move a3,s3
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    ld s4,40(sp)
    ld s5,48(sp)
    addiu sp,sp,96
kc_old:
    j WC_BOTH
    nop
kc_mine:
    lw a0,0xAF8(s0)               # the twin's weapon in the first hand
    move s4,zero                  # the answer of its end (0 = the new weapon gets its method + 0x48 called)
    beq a0,zero,kc_ended
    addiu s5,zero,-1
    lw t7,0x9B4(a0)
    beq t7,zero,kc_e1
    nop
    lh s5,0(t7)
kc_e1:
    sd a0,56(sp)
    jal 0x0019C5D0                # it is ended as the game ends the hero's, BEFORE any file moves
    nop
    move s4,v0
    jal 0x00185A28
    ld a0,56(sp)
    sw zero,0xAF8(s0)
kc_ended:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kc_p2
    nop
    sw s3,0x7E8C(t7)              # PLAYER 1's MENU. His new Keyblade, for kc_load inside the game's routine
    move a0,s1
    move a1,s2
    move a2,zero
    jal 0x00175F68                # the game's routine: his hero's weapon and its files
    move a3,s3
    lui t7,0x000E
    sw zero,0x7E8C(t7)
    lui t8,0x0033
    lhu s3,@KB@(t8)               # the twin's weapon is built again with HIS Keyblade
    b kc_build
    move s2,zero                  # (the game's routine has done its last step itself)
kc_p2:
    jal 0x001703A8                # PLAYER 2's MENU. Only the twin's weapon changes. His old own files go
    addiu a0,zero,2303
    lui t8,0x0033
    lhu t6,@KB@(t8)               # player 1's Keyblade (it waits in the store while player 2's menu is open)
    beq t6,s3,kc_ld               # the same Keyblade now: one set of files
    nop
    jal kc_set
    nop
    sd v0,64(sp)
    move a0,v0
    jal 0x00185890                # the weapon object of the twin's body for the new Keyblade
    move a1,s3
    beq v0,zero,kc_ld
    move a2,v0
    ld a0,64(sp)
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58                # its files: behind player 1's, in the hero's block
    move t0,s5
kc_ld:
    jal 0x00170888                # load now
    move a0,s1
    addiu s2,zero,1               # (the routine's last step is still to do)
kc_build:
    beq s3,zero,kc_last
    nop
    jal kc_set
    nop
    move a0,v0
    jal 0x00185890
    move a1,s3
    beq v0,zero,kc_last
    move a1,v0
    move a0,s0
    jal 0x00176168                # the twin's weapon is built in his hand
    move a2,zero
    bne s4,zero,kc_last
    nop
    lw a0,0xAF8(s0)
    beq a0,zero,kc_last
    nop
    lw t6,0(a0)
    lw t7,72(t6)
    jalr t7                       # (the game's last step for a new weapon)
    nop
kc_last:
    beq s2,zero,kc_out
    nop
    jal 0x00103B38                # (the end of the game's routine)
    nop
    beq v0,zero,kc_out
    nop
    jal 0x001617D8
    nop
kc_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    ld s4,40(sp)
    ld s5,48(sp)
    jr ra
    addiu sp,sp,96

kc_load:                          # call at 0x0017607C (was jal 0x00170888: load now, inside the game's weapon change). a0 = the menu's record, s0 = the weapon set, s5 = a value of the old weapon
    lui t7,0x000E
    lw t6,0x7E8C(t7)              # player 1's new Keyblade (0 = not his menu's change of the first hand with a twin there)
    beq t6,zero,kl_go
    lui t8,0x0033
    lhu a1,@KB@(t8)               # player 2's Keyblade
    beq a1,zero,kl_go
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    bne a1,t6,kl_ask
    nop
    jal 0x001703A8                # both hold the same Keyblade now: player 2's own files go
    addiu a0,zero,2303
    b kl_r
    nop
kl_ask:
    jal 0x00185890                # another one: its files are asked for (again; they move when player 1's files change their size)
    move a0,s0
    beq v0,zero,kl_r
    move a2,v0
    move a0,s0
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58
    move t0,s5
kl_r:
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
kl_go:
    j 0x00170888
    nop
""".replace("@KB@", str(P2KB)).replace("@LW@", str(P2LW)).replace("@KM@", str(P2KM))


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--ownkey" in sys.argv:                                             # sixty-third glue (player 2's own Keyblade)
        assert "--ownitems" in sys.argv and "--no-keychange" not in sys.argv, "--ownkey needs --ownitems and the thirty-third glue"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _c, go_labels = assemble(GO_AT, GO_SRC, {"TICK_NEXT": 0, "GN_CNT": GN_AT})
        labels, n = add_code(KB_AT, KB_END, KB_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "WC_BOTH": WC_AT},
                             "player 2's own Keyblade")

        def jmp2(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["kb_tick"]), "the field's START look-out: first, player 2's Keyblade is made and follows the story")
        hook_base(go_labels["ow_out"] + 4, 0x03E00008, jmp2(labels["kb_swap"]), "player 2's menu opens or goes: his Keyblade and player 1's change places in the hero's record")
        at = [x for x in range(GO_AT, GO_END, 4) if words.get(x) == jmp2(0x001A1214)]
        assert len(at) == 1, at
        hook_base(at[0], jmp2(0x001A1214), jmp2(labels["kb_tview"]), "the view T is made: player 2's Keyblade goes in")
        hook_base(0x000F0344, jal(0x00179FD0), jal(labels["kb_fact"]), "lane E's call of the player factory: noted while it runs")
        hook_game(0x0016F680, jal(0x00188FE0), jal(labels["kb_rec"]), "a body's weapon item: the twin's first hand gets player 2's Keyblade while he is built")
        hook_game(0x0016ECDC, jal(0x0016EF58), jal(labels["kb_req"]), "a body asks for its weapon's files: player 2's Keyblade's files too (number 2303)")
        hook_game(0x001A8B20, jmp2(0x0016FAB0), jmp2(labels["kb_size"]), "the hero's block of the file pool: 256 KB more, for a second Keyblade")
        hook_base(0x002933D0, jmp2(WC_AT), jmp2(labels["kc_menu"]), "the menu's weapon change: first kc_menu (each player's own Keyblade), then glue 33")
        hook_game(0x0017607C, jal(0x00170888), jal(labels["kc_load"]), "the weapon change's load: player 2's files are asked for again or let go")
        n_glue += n + 4

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
