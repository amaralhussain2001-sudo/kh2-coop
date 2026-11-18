r"""One-off (STATE part 147; the user's words 2026-11-18: "finish the 11 9 8 for now", item 9 = look at the partner's gear):
THE EIGHTY-FOURTH GLUE, option --partnerview (needs --ownmenu and --menuowner). Research and design: local\analysis\agent-gear\
(design-partnerview.txt, notes.txt; read-only agent).
HOLD L2 AND PRESS START: the pause menu opens on the PARTNER's gear (Keyblade, armour, accessories, abilities, items, his munny and
bag), read-only. The decision is taken once, when the menu opens; nothing changes places while it is open.
  pv_open (po_open's last word, was j mo_open): with a twin, the player who pressed START (player 1 wins a tie, as mo_open) holds L2
    (his raw held word, physical record [logical record + 0x44], bit 0x100; the logical tables give L1 and L2 the same bit) and
    nothing is swapped (V_MENU2 0) -> V_VIEW (0x000DD800) = the viewer. Viewer 1: V_MENU2 = 1, ow_swap, ow_load (exactly the state of
    player 2's own menu: ms_tick swaps back at the close). Viewer 2: no swap (Sora's record holds player 1's things). Then the NET
    (pv_save: Sora's record +0x00 and +0x14..+0x53, the shortcuts 0x0032F228, 76 bytes at 0x000DD840) and the menu (0x00253180).
    Everything else: mo_open as before.
  pv_tick (head of the field's START look-out, 0x00138538, in front of po_tick): V_VIEW set -> the NET back, V_VIEW = 0, and for
    viewer 2 ow_load (the stats from the record again); then po_tick.
  GATES while V_VIEW is set (the edit points of the menu; each one has only this caller): equip commit (0x002690A4), the two
    ability switches (0x0027874C, 0x00278F8C), using an item (0x002614DC), the item yes/no page's "Yes" (jump table word 0x00373234 ->
    its "No" path), the item refill switch (0x002682F4, 0x0026932C), the Customize settings (entries 0x00273818, 0x00273C40).
  pv_load / pv_new (in front of or_load / or_new): V_VIEW = 0.
Without --partnerview the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_partnerview.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--partnerview" in t:
    raise SystemExit("already done")

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTY-FOURTH GLUE (built only with the option --partnerview, with --ownmenu and --menuowner): HOLD L2 AND PRESS START = THE PAUSE
MENU ON THE PARTNER'S GEAR, READ-ONLY. pv_open (in place of po_open's j mo_open): the START presser holds L2 (raw word bit 0x100) ->
V_VIEW (0x000DD800) = viewer; viewer 1 gets the swap of player 2's own menu (V_MENU2 = 1, ow_swap, ow_load), viewer 2 none; a NET of
76 bytes (Sora's record +0x00, +0x14..+0x53, the shortcuts) at 0x000DD840. pv_tick (head of the START look-out 0x00138538, before
po_tick): the NET back, V_VIEW = 0, ow_load for viewer 2. While V_VIEW is set the menu's edit points do nothing (equip commit, ability
switches, item use and its yes/no "Yes", refill switch, Customize settings). or_load / or_new clear V_VIEW. Room 0x000DD000 ..
0x000DD200 (code), 0x000DD800 .. 0x000DD88C (values).
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eighty-fourth glue (only with --partnerview) ----------------------------------------------------------------
PV_AT = 0x000DD000
PV_END = 0x000DD200
V_VIEW = 0x000DD800                                 # 0 = no partner view; 1 / 2 = the viewer (player 1 / player 2)
PV_NET = 0x000DD840                                 # 19 words: Sora's record +0x00, +0x14..+0x53, the shortcuts 0x0032F228
PV_GATES = (                                        # (address, game word, label): the menu's edit points, jal sites
    (0x002690A4, 0x0C09AAC6, "pv_e1"),              # equip commit 0x0026AB18 (weapon, armour, accessory, item place; every member)
    (0x0027874C, 0x0C09EFDA, "pv_e2a"),             # ability switch 0x0027BF68
    (0x00278F8C, 0x0C09F070, "pv_e2b"),             # ability switch 0x0027C1C0
    (0x002614DC, 0x0C098DDE, "pv_e3"),              # use an item 0x00263778
    (0x002682F4, 0x0C09AC3E, "pv_e4"),              # item refill switch 0x0026B0F8
    (0x0026932C, 0x0C09AC3E, "pv_e4"),
)
PV_SRC = """
pv_open:                          # from po_open's end (was j MO_OPEN). a0 = 0, a1 = -1: the menu call's arguments
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq t6,zero,pv_mo             # one hero: as before
    lui t5,0x0035
    addiu t5,t5,-10560            # controller 1's logical record (0x0034D6C0)
    ld t4,8(t5)
    andi t4,t4,2
    bne t4,zero,pv_who            # player 1 pressed START (he wins a tie, as mo_open)
    addiu t3,zero,1
    ld t4,0x68(t5)
    andi t4,t4,2
    beq t4,zero,pv_mo
    addiu t3,zero,2
    addiu t5,t5,0x60              # controller 2's logical record
pv_who:
    lw t4,0x44(t5)                # its physical record
    beq t4,zero,pv_mo
    nop
    ld t4,0(t4)                   # the raw held word
    andi t4,t4,0x100              # L2
    beq t4,zero,pv_mo
    lui t2,0x000E
    lw t1,0x7E24(t2)              # V_MENU2: player 2's things already in Sora's record?
    bne t1,zero,pv_mo
    lw t1,0x7E28(t2)              # V_HEROREC: Sora's record
    beq t1,zero,pv_mo
    lui t0,0x000E
    sw t3,-10240(t0)              # V_VIEW (0x000DD800) = the viewer
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    addiu t9,zero,1
    bne t3,t9,pv_net              # viewer 2: nothing to swap (Sora's record holds player 1's things)
    nop
    jal OW_SWAP                   # viewer 1: player 2's things into Sora's record, as for player 2's own menu
    sw t9,0x7E24(t2)              # V_MENU2 = 1 (ms_tick swaps back when the field goes on)
    jal OW_LOAD
    nop
pv_net:
    jal pv_save
    nop
    ld a0,8(sp)
    ld a1,16(sp)
    ld ra,0(sp)
    j 0x00253180                  # the menu
    addiu sp,sp,32
pv_mo:
    j MO_OPEN
    nop
pv_save:                          # the NET: [V_HEROREC] +0x00, +0x14..+0x53, the shortcuts -> 0x000DD840 (19 words)
    lui t2,0x000E
    lw t1,0x7E28(t2)
    lui t0,0x000E
    addiu t0,t0,-10176            # 0x000DD840
    lw t3,0(t1)
    sw t3,0(t0)
    addiu t4,t1,0x14
    addiu t5,zero,16
ps_l:
    lw t3,0(t4)
    sw t3,4(t0)
    addiu t4,t4,4
    addiu t5,t5,-1
    bne t5,zero,ps_l
    addiu t0,t0,4
    lui t4,0x0033
    lw t3,-3544(t4)               # 0x0032F228
    sw t3,4(t0)
    lw t3,-3540(t4)
    jr ra
    sw t3,8(t0)
pv_rest:                          # the NET back
    lui t2,0x000E
    lw t1,0x7E28(t2)
    beq t1,zero,pr_out
    lui t0,0x000E
    addiu t0,t0,-10176
    lw t3,0(t0)
    sw t3,0(t1)
    addiu t4,t1,0x14
    addiu t5,zero,16
pr_l:
    lw t3,4(t0)
    sw t3,0(t4)
    addiu t4,t4,4
    addiu t5,t5,-1
    bne t5,zero,pr_l
    addiu t0,t0,4
    lui t4,0x0033
    lw t3,4(t0)
    sw t3,-3544(t4)
    lw t3,8(t0)
    sw t3,-3540(t4)
pr_out:
    jr ra
    nop
pv_tick:                          # from 0x00138538 (was jal PO_TICK): the field's START look-out, every field step
    lui t0,0x000E
    lw t1,-10240(t0)              # V_VIEW
    beq t1,zero,pt_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal pv_rest                   # a partner view was open: the NET back
    sw zero,-10240(t0)            # V_VIEW = 0
    lui t2,0x000E
    lw t1,0x7E24(t2)
    bne t1,zero,pt_ret            # viewer 1: ms_tick swaps back (and loads)
    nop
    jal OW_LOAD                   # viewer 2: the stats from the record again
    nop
pt_ret:
    ld ra,0(sp)
    addiu sp,sp,16
pt_go:
    j PO_TICK
    move a0,zero
pv_e1:
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    j 0x0026AB18
    nop
pv_e2a:
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    j 0x0027BF68
    nop
pv_e2b:
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    j 0x0027C1C0
    nop
pv_e3:
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    j 0x00263778
    nop
pv_e4:
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    j 0x0026B0F8
    nop
pv_c1:                            # entry of 0x00273818 (Customize: item setting)
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    addiu sp,sp,-64               # its first two words
    j 0x00273820
    sd s1,8(sp)
pv_c2:                            # entry of 0x00273C40 (Customize: a setting of the record + 0xF4)
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pv_no
    nop
    addiu sp,sp,-16
    j 0x00273C48
    sd s0,0(sp)
pv_no:
    jr ra                         # a partner view: nothing is changed
    move v0,zero
pv_e3b:                           # the item yes/no page's "Yes" (jump table word 0x00373234)
    lui t8,0x000E
    lw t8,-10240(t8)
    bne t8,zero,pe3_no
    nop
    j 0x00261AF0
    nop
pe3_no:
    j 0x00261AC0                  # its "No"
    nop
pv_load:                          # 0x00240B84 (was j OR_LOAD)
    lui t8,0x000E
    j OR_LOAD
    sw zero,-10240(t8)
pv_new:                           # 0x00105770 (was jal OR_NEW)
    lui t8,0x000E
    j OR_NEW
    sw zero,-10240(t8)
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--partnerview" in sys.argv:                                        # eighty-fourth glue (the partner's gear, read-only)
        assert "--ownmenu" in sys.argv and "--menuowner" in sys.argv, "--partnerview needs --ownmenu and --menuowner"
        assert V_VIEW == 0x000E0000 - 10240 and PV_NET == 0x000E0000 - 10176
        _c, rm_pv = assemble(RM_AT, RM_SRC, {})
        j_mo = (2 << 26) | ((rm_pv["mo_open"] >> 2) & 0x3FFFFFF)
        po_end = [a for a in range(MO_AT, MO_END, 4) if words.get(a) == j_mo]
        assert len(po_end) == 1, "po_open's j mo_open: %r" % po_end
        tick_w = words[0x00138538]
        assert (tick_w >> 26) == 3, "0x00138538 is not a jal"
        lw_l, lw_n = words[0x00240B84], words[0x00105770]
        assert (lw_l >> 26) == 2 and (lw_n >> 26) == 3, "or_load / or_new hooks are not j / jal"
        syms = {"MO_OPEN": rm_pv["mo_open"], "OW_SWAP": rm_pv["ow_swap"], "OW_LOAD": rm_pv["ow_load"],
                "PO_TICK": (tick_w & 0x3FFFFFF) << 2, "OR_LOAD": (lw_l & 0x3FFFFFF) << 2, "OR_NEW": (lw_n & 0x3FFFFFF) << 2}
        assert syms["OR_LOAD"] == rm_pv["or_load"] and syms["OR_NEW"] == rm_pv["or_new"]
        code, labels = assemble(PV_AT, PV_SRC, syms)
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert PV_AT + 4 * len(code) <= PV_END, "the eighty-fourth glue does not fit"
        clash = [a for a in words if PV_AT <= a < PV_END or V_VIEW <= a < PV_NET + 76]
        assert not clash, "patch words in the eighty-fourth glue's room: %08X" % clash[0]
        for i, w in enumerate(code):
            a = PV_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (the partner's gear, read-only)"
        hook_base(po_end[0], j_mo, (2 << 26) | ((labels["pv_open"] >> 2) & 0x3FFFFFF), "START: with L2 held, the partner's gear (read-only)")
        hook_base(0x00138538, tick_w, jal(labels["pv_tick"]), "the field's START look-out: first, a partner view's net goes back")
        hook_base(0x00240B84, lw_l, (2 << 26) | ((labels["pv_load"] >> 2) & 0x3FFFFFF), "a save file is loaded: no partner view")
        hook_base(0x00105770, lw_n, jal(labels["pv_new"]), "the save data are made new: no partner view")
        for a, w0, label in PV_GATES:
            hook_game(a, w0, jal(labels[label]), "a menu edit point: nothing in a partner view (" + label + ")")
        hook_game(0x00373234, 0x00261AF0, labels["pv_e3b"], "the item yes/no page's Yes: its No in a partner view")
        hook_game(0x00273818, 0x27BDFFC0, (2 << 26) | ((labels["pv_c1"] >> 2) & 0x3FFFFFF), "Customize (item setting): nothing in a partner view")
        hook_game(0x0027381C, 0xFFB10008, 0, "(pv_c1 does the two words)")
        hook_game(0x00273C40, 0x27BDFFF0, (2 << 26) | ((labels["pv_c2"] >> 2) & 0x3FFFFFF), "Customize (record + 0xF4): nothing in a partner view")
        hook_game(0x00273C44, 0xFFB00000, 0, "(pv_c2 does the two words)")
        n_glue += len(code) + 11

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-fourth glue (--partnerview) added")
