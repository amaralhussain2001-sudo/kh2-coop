"""One-off: tools/merge/merge_v7.py, plan row 39 stage 1a: the forty-eighth glue (--ownrec) gets its second form
(record T is only a VIEW; player 2's armour and accessory places live in the source record's places 5 to 8), and
the FORTY-NINTH GLUE (--ownmenu, needs --ownrec): while PLAYER 2's pause menu is open the hero's places and his
change places. The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownmenu.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "mo_open" in s:
    raise SystemExit("already there")

# ---- the header text of the forty-eighth glue: its second form
a = s.index("FORTY-EIGHTH GLUE (NOT in builds 13 / 14; built only with the option --ownrec)")
b = s.index("  python -I tools/merge/merge_v7.py [outDir]")
hdr = '''FORTY-EIGHTH GLUE (NOT in builds 13 / 14; built only with the option --ownrec): THE SECOND HERO'S UNIT SLOT READS A
CHARACTER RECORD OF HIS OWN (plan row 39 "own gear for each player", stage 1a; job 11 of the eighth round).
What is there (lane D, `tools/lane-d/make_ownhp2.py`): both heroes' unit slots point at the SAME character record
(Sora's, save + 0x24F0 = 0x0032E020, 0x114 bytes; slot + 0x244); only the current HP / MP bytes are the twin's own.
The game loads a slot's stats, abilities and equipment bonuses from that record in 0x001A11E0(slot, record or 0)
(experiments e1a / e1b / e1c: a second record in the twin's slot works; run or1: the first form of this glue).
The record has 8 armour places (+ 0x14 .. + 0x23) and 8 accessory places (+ 0x24 .. + 0x33); a hero's counts
(+ 0x10 / + 0x11) never pass 4. PLAYER 2'S FOUR ARMOUR PLACES ARE + 0x1C .. + 0x23 AND HIS FOUR ACCESSORY PLACES
+ 0x2C .. + 0x33 OF THAT SAME RECORD: saved, loaded and kept by Continue with the game's own save.
Now t_load (the jump at 0x001A1200, the stat loader's "which record" step): for the twin's slot (lane D's mark, bit
31 of slot + 0x250) the record is T (0x000E7D00, 0x114 bytes; 0x000E7E20 = the record it shows): every time T = a
full copy of the source record, with player 2's places where the hero's are and the hero's where player 2's
are. (While player 2's menu is open, forty-ninth glue, the source has them changed already: a plain copy.)
The slot's pointer (slot + 0x244) is set to T. Everything else is common: Keyblade, abilities, item places.

FORTY-NINTH GLUE (built only with --ownmenu; it needs --ownrec): PLAYER 2 CHOOSES HIS ARMOUR AND ACCESSORIES IN THE
PAUSE MENU WHEN HE OPENED IT.
The menu only knows "Sora's record". START is looked for at 0x00138538 (second glue: on both controllers) and the
main menu is opened by the call at 0x00138574 -> 0x00253180(0, -1).
 mo_open (that call): when there is a twin and START was pressed on controller 2 and not on controller 1, the
   hero's places 1 to 4 and player 2's places 5 to 8 change places in the source record (armour and accessories),
   a flag is set (0x000E7E24) and player 1's slot loads its stats again (lane D's D6 then loads the twin's), so
   the menu shows and edits PLAYER 2's places with his numbers.
 ms_tick (the call at 0x00138538, each step the field looks for START): when the flag is set and the main menu's
   module (0, asked with 0x00103428) is gone, the places change back, the flag is cleared and player 1's slot
   loads its stats again (and with it the twin's).
The bag is common: both players equip from the same stock.

'''
s = s[:a] + hdr + s[b:]
x = "[--ownrec]"
assert s.count(x) == 1
s = s.replace(x, "[--ownrec [--ownmenu]]")

# ---- the routine of the forty-eighth glue: its second form
a = s.index('RT_SRC = """')
b = s.index('"""\nRT_HOOK')
new_rt = '''RT_SRC = """
t_load:                           # jump at 0x001A1200 (was: bne a1,zero,0x001A1214 / daddu s1,a1,zero). a0 = the slot
    lw t7,0x250(a0)
    bltz t7,tl_twin               # lane D's mark: the second hero's slot
    nop
tl_game:
    bne a1,zero,tl_have
    daddu s1,a1,zero
    j 0x001A1208
    nop
tl_have:
    j 0x001A1214
    nop
tl_twin:
    lui t6,0x000E
    ori t6,t6,0x7D00              # record T (a view)
    lui t5,0x000E
    bne a1,zero,tl_s1
    lw t4,0x7E20(t5)              # the record T shows
    lw a1,0x244(a0)               # no record given: the slot's own
    beq a1,zero,tl_game           # none: as the game
    nop
tl_s1:
    bne a1,t6,tl_s2
    nop
    move a1,t4                    # the slot's record is T: the source is the remembered one
    beq a1,zero,tl_use            # (cannot be) T without a source: use it as it is
    nop
tl_s2:
    sw a1,0x7E20(t5)              # the source of the view
    addiu t3,zero,0x114           # T = all of the source ...
    move t2,a1
    move t1,t6
tl_cp:
    lw t0,0(t2)
    sw t0,0(t1)
    addiu t3,t3,-4
    addiu t2,t2,4
    bgtz t3,tl_cp
    addiu t1,t1,4
    lw t3,0x7E24(t5)              # player 2's menu is open: the places have changed places in the source already
    bne t3,zero,tl_use
    nop
    lw t0,0x1C(a1)                # ... with PLAYER 2'S armour places (+ 0x1C .. + 0x23) where the hero's are
    lw t1,0x20(a1)
    lw t2,0x14(a1)
    lw t3,0x18(a1)
    sw t0,0x14(t6)
    sw t1,0x18(t6)
    sw t2,0x1C(t6)
    sw t3,0x20(t6)
    lw t0,0x2C(a1)                # and his accessory places (+ 0x2C .. + 0x33)
    lw t1,0x30(a1)
    lw t2,0x24(a1)
    lw t3,0x28(a1)
    sw t0,0x24(t6)
    sw t1,0x28(t6)
    sw t2,0x2C(t6)
    sw t3,0x30(t6)
tl_use:
    sw t6,0x244(a0)               # the twin's slot reads the view
    j 0x001A1214
    daddu s1,t6,zero
'''
s = s[:a] + new_rt + s[b:]

# ---- the forty-ninth glue
i = s.index("def main():")
src = '''# ---- forty-ninth glue (only with --ownmenu) ----------------------------------------------------------------
RM_AT = 0x000E9A00
RM_END = 0x000E9C00
V_MENU2 = 0x000E7E24                               # 1 while player 2's pause menu is open (the places have changed places)
RM_SRC = """
ow_swap:                          # the hero's places 1-4 and player 2's places 5-8 change places in the source record
    lui t5,0x000E
    lw t4,0x7E20(t5)              # the record the twin's view shows (Sora's, Roxas's ...)
    beq t4,zero,os_out
    addiu t3,zero,2               # twice: the armour block (+ 0x14), the accessory block (+ 0x24)
    addiu t4,t4,0x14
os_blk:
    lw t0,0(t4)
    lw t1,4(t4)
    lw t2,8(t4)
    lw t9,12(t4)
    sw t2,0(t4)
    sw t9,4(t4)
    sw t0,8(t4)
    sw t1,12(t4)
    addiu t3,t3,-1
    bgtz t3,os_blk
    addiu t4,t4,0x10
os_out:
    jr ra
    nop
ow_load:                          # player 1's slot writes back and loads its stats again (lane D's D6: the twin's too)
    addiu sp,sp,-32
    sd ra,0(sp)
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,ol_out
    nop
    lw a0,0x48C(t4)               # his unit slot
    beq a0,zero,ol_out
    nop
    sd a0,8(sp)
    jal 0x001A1840
    nop
    ld a0,8(sp)
    jal 0x001A11E0
    move a1,zero
ol_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
mo_open:                          # from 0x00138574 (was jal 0x00253180): START opens the main menu. a0 = 0, a1 = -1
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,mo_go
    lui t5,0x0035
    addiu t5,t5,-10560            # 0x0034D6C0: logical controller 0; controller 1 is 0x60 further
    ld t4,8(t5)                   # pressed, player 1's
    andi t4,t4,0x2
    bne t4,zero,mo_go             # player 1 pressed START (or both did): his menu
    ld t4,0x68(t5)
    andi t4,t4,0x2
    beq t4,zero,mo_go             # (not player 2 either)
    lui t3,0x000E
    lw t2,0x7E24(t3)
    bne t2,zero,mo_go             # (never twice)
    lw t2,0x7E20(t3)
    beq t2,zero,mo_go             # the twin has no view yet
    addiu t1,zero,1
    sw t1,0x7E24(t3)              # player 2's menu is open
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal ow_swap
    nop
    jal ow_load
    nop
    ld a0,8(sp)
    ld a1,16(sp)
    ld ra,0(sp)
    addiu sp,sp,32
mo_go:
    j 0x00253180
    nop
ms_tick:                          # from 0x00138538 (the second glue's jal pad_both): each step the field looks for START
    lui t3,0x000E
    lw t2,0x7E24(t3)
    beq t2,zero,ms_go             # player 2's menu is not open
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00103428                # is the main menu's module (0) still there?
    move a0,zero
    bne v0,zero,ms_keep
    nop
    jal ow_swap                   # gone: the places change back
    nop
    lui t3,0x000E
    jal ow_load
    sw zero,0x7E24(t3)
ms_keep:
    ld ra,0(sp)
    addiu sp,sp,16
ms_go:
    j 0x000F4740                  # the second glue's pad_both
    move a0,zero
"""
RM_OPEN = (0x00138574, 0x0C094C60)                 # jal 0x00253180
RM_TICK = (0x00138538, 0x0C03D1D0)                 # the base patch: jal pad_both (0x000F4740)


'''
s = s[:i] + src + s[i:]
e = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(e) == 1
step = '''    if "--ownmenu" in sys.argv:                                            # forty-ninth glue (plan row 39; not in builds 13 / 14)
        assert "--ownrec" in sys.argv, "--ownmenu needs --ownrec"
        labels, n = add_code(RM_AT, RM_END, RM_SRC, {}, "player 2's pause menu shows and edits his own armour and accessory places")
        a, w0 = RM_OPEN
        hook_game(a, w0, jal(labels["mo_open"]), "START opens the main menu: when player 2 pressed it, the places change places first")
        a, w0 = RM_TICK
        hook_base(a, w0, jal(labels["ms_tick"]), "the field looks for START: first, has player 2's menu gone? (then the second glue's pad_both)")
        n_glue += n + 1

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
