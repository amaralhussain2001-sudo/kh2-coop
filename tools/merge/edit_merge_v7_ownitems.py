"""One-off: tools/merge/merge_v7.py gets the SIXTY-SECOND GLUE (built only with --ownitems, with --ownrec --ownmenu
--ownabil --norec --itemsync): PLAYER 2'S OWN ITEM PLACES, HIS OWN STOCK OF THE SEVEN FIGHT ITEMS, HIS OWN
SHORTCUTS; AND EVERY THING THE GAME GIVES IS THERE FOR EACH PLAYER (plan row 39, the rest; ninth round, part 89).

Read in the program (part 88 and part 89):
 - every change of the bag goes through two routines: add 0x001A32C8(item, count) (called only from "give"
   0x001A3188 at 0x001A31FC, and from 0x001D626C) and take 0x001A34E0(item, count); the menu's equip routines
   (0x0026ACB0 .. 0x0026AFFF) move a thing with give(old, 100) + take-away(new, 100);
 - a use in a fight: 0x00176E78(user, item, flag) asks the user's character number (the call at 0x00176EA4) and
   takes the item out of THAT RECORD's places (0x001A3458); when it answers 0 the item does nothing;
 - the game fills empty places from the bag (0x001A3710, one caller: 0x00253BDC, the pause menu);
 - the shortcut list of a hero's command menu is built at 0x001BED48 from the four shorts at save + 0x36F8;
 - a guest who leaves the party has all his places emptied into the bag (0x001D94F8 -> 0x001D9630).
WHERE PLAYER 2'S THINGS LIVE: King Mickey's record (0x0032E35C; his counts of places are 0 / 0 / 0 and neither the
player-parameter table nor the bonus table ever gives him a place: tools/own/plrp_table.py, bons_table.py):
 + 0x14 his eight item places (bytes), + 0x1C his eight refill entries (bytes), + 0x24 his stock of the items 1 to
 7 (bytes), + 0x2C his four shortcuts (shorts), + 0x44 the mark 0x5033. (+ 0x34 .. + 0x3F: his ability switches,
 glue 58. + 0x40 / + 0x42: kept for his Keyblade.)
The routines:
 oi_init   no mark: his places, refill entries, stock and shortcuts are made = player 1's (a full copy).
 oi_view   the twin's view T (glue 48) gets HIS places and refill entries (so his command menu lists his).
 oi_use    (the call at 0x00176EA4) the twin uses an item: it leaves HIS place; player 1's are not touched.
 oi_refill (the call at 0x00253BDC) after the game's refill, the other player's empty places are filled from the
           other player's stock.
 oi_swap   (the end of glue 58's ab_swap) while player 2's pause menu is open his places, refill entries, stock
           and shortcuts stand where the game's menu reads and writes them (Sora's record, the bag's first seven
           bytes, save + 0x36F8); player 1's wait in the store.
 oi_gain / oi_gain2 (the calls at 0x001A31FC and 0x001A3298) THE GAME GIVES A THING (a chest, a drop, a prize, a
           story gift, a purchase, a synthesis; NOT a move of the menu, 0x0026AC00 .. 0x0026AFFF, not a place
           given up, 0x00188A00, not a leaving guest's things, 0x001D9664): a fight item goes to player 2 as well
           (into an empty place of his, else into his stock); a Keyblade, an armour or an accessory goes into the
           common bag TWICE (one for each player).
 oi_sc     (0x001A3430) a new spell that takes an empty shortcut of player 1's takes player 2's too, if empty.
 sc_base   (0x001BED98) the twin's command menu reads HIS four shortcuts.
The wallet stays one: a purchase gives the thing to both players, so nobody pays twice.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownitems.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "oi_init" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTY-SECOND GLUE (built only with the option --ownitems, with --ownrec --ownmenu --ownabil --norec --itemsync):
PLAYER 2'S OWN ITEM PLACES, HIS OWN STOCK OF THE SEVEN FIGHT ITEMS, HIS OWN SHORTCUTS; EVERY THING THE GAME GIVES
IS THERE FOR EACH PLAYER (plan row 39). His things live in King Mickey's record (0x0032E35C + 0x14 places, + 0x1C
refill entries, + 0x24 stock, + 0x2C shortcuts, + 0x44 the mark 0x5033). oi_init makes them from player 1's;
oi_view puts his places into the twin's view T; oi_use takes a used item out of HIS place (0x00176EA4); oi_refill
fills the other player's places from his own stock (0x00253BDC); oi_swap puts his things where the pause menu
reads them while HIS menu is open; oi_gain / oi_gain2 (0x001A31FC, 0x001A3298): a thing the game gives (not a
move of the menu, not a place given up, not a leaving guest's things) goes to both: a fight item to player 2's
places or stock as well, a Keyblade / armour / accessory twice into the common bag; oi_sc / sc_base: shortcuts.

'''
s = s.replace(a, hdr + a)
b = " [--itemsync]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--ownitems]")

i = s.index("def main():")
src = '''# ---- sixty-second glue (only with --ownitems) ---------------------------------------------------------------
GO_AT = 0x000EC140
GO_END = 0x000EC700
P2B = 0x0032E35C                                   # King Mickey's record: player 2's own things live in its places
P2PL = P2B + 0x14 - 0x00330000                     # his eight item places (bytes); + 8: his eight refill entries
P2ST = P2B + 0x24 - 0x00330000                     # his stock of the fight items 1 .. 7 (bytes)
P2SC = P2B + 0x2C - 0x00330000                     # his four shortcuts (shorts)
P2MARK = P2B + 0x44 - 0x00330000                   # 0x5033 = his item things are made
BAG_LO = 0x0032F0B0 - 0x00330000                   # the bag (save + 0x3580); its first seven bytes = the fight items
SC_LO = 0x0032F228 - 0x00330000                    # the four shortcuts (save + 0x36F8)
GO_SRC = """
oi_init:                          # no mark: player 2's item places, refill entries, stock and shortcuts are made = player 1's. Out: t7 = 1 when they are there
    lui t8,0x0033
    lhu t0,@MARK@(t8)
    addiu t1,zero,0x5033
    beq t0,t1,oi_ok
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record (noted by glue 48)
    beq t9,zero,oi_no
    addiu t2,zero,8
    addiu t3,t8,@PL@
    addiu t4,t9,0x34
oi_c1:
    lhu t0,0(t4)                  # a place
    sb t0,0(t3)
    lhu t0,0x10(t4)               # its refill entry
    sb t0,8(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,oi_c1
    addiu t4,t4,2
    addiu t2,zero,7               # the stock = the bag's seven fight items
    addiu t3,t8,@ST@
    addiu t4,t8,@BAG@
oi_c2:
    lbu t0,0(t4)
    sb t0,0(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,oi_c2
    addiu t4,t4,1
    lw t0,@SC@(t8)                # the four shortcuts
    sw t0,@P2SC@(t8)
    lw t0,@SC4@(t8)
    sw t0,@P2SC4@(t8)
    sh t1,@MARK@(t8)
oi_ok:
    jr ra
    addiu t7,zero,1
oi_no:
    jr ra
    move t7,zero

oi_view:                          # the twin's view T gets player 2's item places and refill entries (not while his menu is open: T is the record then)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,ov_out
    lw t0,0x7E20(t9)              # the record T shows
    lw t1,0x7E28(t9)              # the hero's record
    bne t0,t1,ov_out              # T is another body's (King Mickey): no places of player 2's
    nop
    jal oi_init
    nop
    beq t7,zero,ov_out
    lui t8,0x0033
    lui t9,0x000E
    ori t9,t9,0x7D00              # T
    addiu t3,t8,@PL@
    addiu t2,zero,8
ov_l:
    lbu t0,0(t3)
    sh t0,0x34(t9)
    lbu t0,8(t3)
    sh t0,0x44(t9)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ov_l
    addiu t9,t9,2
ov_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_tview:                         # jump at the end of glue 58's ab_view (was j 0x001A1214; its delay slot: s1 = T). a0 = the twin's slot
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_view
    nop
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    j 0x001A1214
    addiu sp,sp,32

oi_list:                          # jump at 0x001BE9DC (in the place of glue 61's gi_sync). v0 = the record the item list is built from
    lui t7,0x000E
    ori t6,t7,0x7D00
    bne v0,t6,ol_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd v0,8(sp)
    jal oi_view
    nop
    ld v0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
ol_go:
    j GN_CNT
    nop

oi_use:                           # call at 0x00176EA4 (was jal 0x0016A070: the user's character number). a0 = the user, s0 = the item
    lui t7,0x000F
    lw t6,0x05CC(t7)
    bne a0,t6,ou_game             # not the twin: the game's way
    nop
    lw t5,0x48C(a0)               # his unit slot
    beq t5,zero,ou_game
    nop
    lw t4,0x254(t5)               # whose slot: only a hero (1 = Sora, 14 = Roxas) has places of player 2's
    addiu t3,zero,1
    beq t4,t3,ou_hero
    addiu t3,zero,14
    bne t4,t3,ou_game
    nop
ou_hero:
    lui t7,0x000E
    lw t3,0x7E24(t7)
    bne t3,zero,ou_game           # (his menu is open: cannot be in a fight)
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t2,zero,0x5033
    bne t3,t2,ou_game
    ori t9,t7,0x7D00              # T
    lbu t2,0x12(t9)               # the count of item places
    addiu t2,t2,-1
    bltz t2,ou_none
    addiu t3,t8,@PL@
    addu t3,t3,t2                 # from the last place down, as the game does
    sll t4,t2,1
    addu t9,t9,t4
ou_l:
    lbu t5,0(t3)
    bne t5,s0,ou_n
    nop
    sb zero,0(t3)                 # it leaves HIS place
    sh zero,0x34(t9)              # and his view
    j 0x00176EB8                  # the routine's own way out
    addiu v0,zero,1               # taken
ou_n:
    addiu t2,t2,-1
    addiu t3,t3,-1
    bgez t2,ou_l
    addiu t9,t9,-2
ou_none:
    j 0x00176EB8
    move v0,zero                  # he has none: nothing happens (as the game answers)
ou_game:
    j 0x0016A070
    nop

oi_refill:                        # call at 0x00253BDC (was jal 0x001A3710: the game fills empty places from the bag)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001A3710                # the places that stand in the records now (player 1's, or player 2's while his menu is open)
    nop
    jal oi_init
    nop
    beq t7,zero,or_out
    lui t8,0x0033
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record: the count of places
    beq t9,zero,or_out
    nop
    lbu t2,0x12(t9)
    blez t2,or_out
    addiu t3,t8,@PL@              # the places in the store: the OTHER player's
or_l:
    lbu t0,8(t3)                  # the refill entry
    beq t0,zero,or_n
    lbu t1,0(t3)
    bne t1,zero,or_n              # the place is not empty
    sltiu t4,t0,8
    beq t4,zero,or_n
    addu t4,t8,t0
    lbu t5,@STM1@(t4)             # his stock of that item
    blez t5,or_n
    addiu t5,t5,-1
    sb t5,@STM1@(t4)
    sb t0,0(t3)
or_n:
    addiu t2,t2,-1
    bgtz t2,or_l
    addiu t3,t3,1
    jal oi_view
    nop
or_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_swap:                          # jump at the end of glue 58's ab_swap (was jr ra): player 2's menu opens or goes
    addiu sp,sp,-16
    sd ra,0(sp)
    jal oi_init
    nop
    beq t7,zero,ow_out
    lui t8,0x0033
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record
    beq t9,zero,ow_out
    addiu t2,zero,8
    addiu t3,t8,@PL@
ow_a:
    lhu t0,0x34(t9)               # the item places
    lbu t1,0(t3)
    sh t1,0x34(t9)
    sb t0,0(t3)
    lhu t0,0x44(t9)               # the refill entries
    lbu t1,8(t3)
    sh t1,0x44(t9)
    sb t0,8(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ow_a
    addiu t9,t9,2
    addiu t2,zero,7               # the stock of the seven fight items
    addiu t3,t8,@ST@
    addiu t4,t8,@BAG@
ow_b:
    lbu t0,0(t4)
    lbu t1,0(t3)
    sb t1,0(t4)
    sb t0,0(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ow_b
    addiu t4,t4,1
    lw t0,@SC@(t8)                # the four shortcuts
    lw t1,@P2SC@(t8)
    sw t1,@SC@(t8)
    sw t0,@P2SC@(t8)
    lw t0,@SC4@(t8)
    lw t1,@P2SC4@(t8)
    sw t1,@SC4@(t8)
    sw t0,@P2SC4@(t8)
ow_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_p2get:                         # in: a1 = a fight item (1 .. 7). The other player gets one too: into an empty place of his, else into his stock
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t4,zero,0x5033
    bne t3,t4,pg_out
    sltiu t3,a1,8
    beq t3,zero,pg_out
    lui t9,0x000E
    lw t7,0x7E24(t9)
    bne t7,zero,pg_stock          # (player 2's menu is open: the store holds player 1's things; his stock gets it)
    lw t9,0x7E28(t9)              # the hero's record: the count of places
    beq t9,zero,pg_stock
    nop
    lbu t2,0x12(t9)
    blez t2,pg_stock
    addiu t3,t8,@PL@
    move t6,zero
pg_l:
    lbu t0,0(t3)
    bne t0,zero,pg_n              # not empty
    lbu t1,8(t3)
    beq t1,a1,pg_put              # empty, and kept for this item
    nop
    beq t1,zero,pg_put            # empty, and kept for nothing
    nop
pg_n:
    addiu t6,t6,1
    slt t0,t6,t2
    bne t0,zero,pg_l
    addiu t3,t3,1
pg_stock:
    addu t5,t8,a1
    lbu t6,@STM1@(t5)
    sltiu t3,t6,99
    beq t3,zero,pg_out
    addiu t6,t6,1
    jr ra
    sb t6,@STM1@(t5)
pg_put:
    sb a1,0(t3)
    lui t9,0x000E                 # the twin's view shows it at once (when it is the hero's view)
    lw t0,0x7E20(t9)
    lw t1,0x7E28(t9)
    bne t0,t1,pg_out
    ori t9,t9,0x7D00
    sll t6,t6,1
    addu t9,t9,t6
    sh a1,0x34(t9)
pg_out:
    jr ra
    nop

oi_gain:                          # call at 0x001A31FC (was jal 0x001A32C8: add to the bag). a0 = the item, a1 = 1, s2 = its table entry, 40(sp) = who called "give"
    ld t0,40(sp)
    lui t1,0x0027
    addiu t1,t1,-21504            # 0x0026AC00
    sltu t2,t0,t1
    bne t2,zero,og_w1
    addiu t1,t1,0x400             # 0x0026B000
    sltu t2,t0,t1
    bne t2,zero,og_go             # the menu moves a thing from a place into the bag: as the game
    nop
og_w1:
    lui t1,0x0019
    addiu t1,t1,-30208            # 0x00188A00
    beq t0,t1,og_go               # a place given up when the count shrinks: as the game
    lui t1,0x001E
    addiu t1,t1,-27036            # 0x001D9664
    beq t0,t1,og_go               # a leaving guest's things: as the game
    lbu t2,2(s2)                  # THE GAME GIVES A THING. Its type:
    bne t2,zero,og_eq
    addiu t3,zero,2
    addiu sp,sp,-32               # a fight item: the other player gets one too
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_p2get
    move a1,a0
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    b og_go
    addiu sp,sp,32
og_eq:
    beq t2,t3,og_two              # a Keyblade
    addiu t3,zero,14
    beq t2,t3,og_two              # an armour
    addiu t3,zero,15
    bne t2,t3,og_go               # an accessory
    nop
og_two:
    lhu t3,0x12(s2)               # its place in the bag
    lui t8,0x0033
    addu t3,t3,t8
    lbu t4,@BAG@(t3)
    sltiu t4,t4,98
    beq t4,zero,og_go
    nop
    addiu a1,zero,2               # one for each player
og_go:
    j 0x001A32C8
    nop

oi_gain2:                         # call at 0x001A3298 (was jal 0x00188A28: put into a place). a0 = the record, a1 = the item, s0 = the character number
    addiu t3,zero,1
    beq s0,t3,o2_hero
    addiu t3,zero,14
    bne s0,t3,o2_go               # a helper's place: his things are common
    nop
o2_hero:
    addiu sp,sp,-32               # the game gives the hero a fight item: the other player gets one too
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_p2get
    nop
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
o2_go:
    j 0x00188A28
    nop

oi_sc:                            # jump at 0x001A3430 (was b 0x001A3410; its delay slot writes player 1's shortcut: sh t7,8(t4)). t4 = save + 0x36F0 + 2 x the place
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t5,zero,0x5033
    bne t3,t5,oc_out
    lui t9,0x000E
    lw t9,0x7E24(t9)
    bne t9,zero,oc_out
    addiu t5,t8,@SCM8@            # save + 0x36F0
    subu t5,t4,t5                 # 2 x the place
    addu t5,t5,t8
    lhu t3,@P2SC@(t5)
    bne t3,zero,oc_out            # player 2's shortcut there is taken
    nop
    sh t7,@P2SC@(t5)
oc_out:
    j 0x001A3410
    nop

sc_base:                          # call at 0x001BED98 (was addiu t7,t7,-17616: the save's base; the next line adds 0x36F8). s4 = the control object
    lui t7,0x0033
    addiu t7,t7,-17616
    lui t5,0x000F
    lw t5,0x05CC(t5)              # the twin
    beq t5,zero,sb_out
    lw t4,2528(s4)                # this menu's hero
    bne t4,t5,sb_out
    lui t5,0x0033
    lhu t4,@MARK@(t5)
    addiu t3,zero,0x5033
    bne t4,t3,sb_out
    lui t3,0x000E
    lw t3,0x7E24(t3)
    bne t3,zero,sb_out
    nop
    addiu t7,t5,@P2SCB@           # so that + 0x36F8 is player 2's four shortcuts
sb_out:
    jr ra
    nop

oi_tick:                          # from 0x00138538 (each step the field looks for START): his things are made as soon as the hero's record is known
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,ot_go
    nop
    jal oi_init
    nop
ot_go:
    ld ra,0(sp)
    addiu sp,sp,16
    j TICK_NEXT
    move a0,zero
""".replace("@MARK@", str(P2MARK)).replace("@PL@", str(P2PL)).replace("@STM1@", str(P2ST - 1)).replace("@ST@", str(P2ST)) \\
   .replace("@P2SC4@", str(P2SC + 4)).replace("@P2SCB@", str(P2SC - 0x36F8)).replace("@P2SC@", str(P2SC)) \\
   .replace("@BAG@", str(BAG_LO)).replace("@SCM8@", str(SC_LO - 8)).replace("@SC4@", str(SC_LO + 4)).replace("@SC@", str(SC_LO))


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--ownitems" in sys.argv:                                           # sixty-second glue (player 2's own item places, stock and shortcuts; every gain for each)
        assert all(o in sys.argv for o in ("--ownrec", "--ownmenu", "--ownabil", "--norec", "--itemsync")), "--ownitems needs --ownrec --ownmenu --ownabil --norec --itemsync"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _c, ga_labels = assemble(GA_AT, GA_SRC, {})
        labels, n = add_code(GO_AT, GO_END, GO_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "GN_CNT": GN_AT},
                             "player 2's own item places, stock and shortcuts; every thing the game gives is there for each player")

        def jmp(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["oi_tick"]), "the field's START look-out: first, are player 2's item things made")
        hook_base(ga_labels["as_out"], 0x03E00008, jmp(labels["oi_swap"]), "player 2's menu opens or goes: his item places, stock and shortcuts change places too")
        at = [x for x in range(GA_AT, GA_END, 4) if words.get(x) == jmp(0x001A1214)]
        assert len(at) == 1, at
        hook_base(at[0], jmp(0x001A1214), jmp(labels["oi_tview"]), "the view T is made: player 2's item places go in")
        hook_base(0x001BE9DC, jmp(GI_AT), jmp(labels["oi_list"]), "the command menu counts the hero's item places: first, the view gets player 2's places")
        hook_game(0x00176EA4, 0x0C05A81C, jal(labels["oi_use"]), "an item is used: the twin's leaves HIS place")
        hook_game(0x00253BDC, jal(0x001A3710), jal(labels["oi_refill"]), "the game fills empty places: the other player's too, from his own stock")
        hook_game(0x001A31FC, jal(0x001A32C8), jal(labels["oi_gain"]), "a thing goes into the bag: what the game gives is there for each player")
        hook_game(0x001A3298, jal(0x00188A28), jal(labels["oi_gain2"]), "a fight item goes into the hero's place: the other player gets one too")
        hook_game(0x001A3430, 0x1000FFF7, jmp(labels["oi_sc"]), "a new spell takes an empty shortcut: player 2's too")
        hook_game(0x001BED98, 0x25EFBB30, jal(labels["sc_base"]), "the shortcut list of a command menu: the twin's is built from HIS four shortcuts")
        n_glue += n + 6

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
