r"""One-off (STATE part 141; the user's words 2026-11-17: "when i open the menu i should click the buttons and if he open it he
should controll right? same for npc etc", "go", "we don't need to do the safety because both going play toghther always"):
THE SEVENTY-NINTH GLUE, option --menuowner: THE PLAYER WHO OPENS A SCREEN ALONE CONTROLS IT.
Adds to tools/merge/merge_v7.py: the header paragraph, the glue's source (MO_AT .. MO_END) and the builder block (after the
seventy-eighth glue). Without --menuowner the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_menuowner.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--menuowner" in t:
    raise SystemExit("already done")

HEADER_OLD = """(as build 23), every other call takes the tag (none: player 1's, as before). Room 0x000EF000 .. 0x000EF400 (glue 77's).
"""
HEADER_NEW = HEADER_OLD + """
SEVENTY-NINTH GLUE (built only with the option --menuowner, needs --ownmenu and --ownwallet): THE PLAYER WHO OPENS A SCREEN
ALONE CONTROLS IT. The second glue's pad_both (0x000F4740) gave every screen that asks it (text boxes, the main menu and its 49
pages' routine, the rules screens, the world map, the shop's quantity box, the script's button tests) both controllers OR-ed,
so while one player was in a shop or a talk the other's buttons moved his cursor, bought or closed it. Now pad_both's first
word jumps to po_pad: when a player OWNS the screen (V_OWNER 0x000DE800: 1 = player 1, 2 = player 2), the record is that
player's logical controller alone; nobody (0) = both, as before. The field's START look-out (the call at 0x00138538) and the
command menu's first button (0x0013C798) always hear both. The owner is set by po_open (START opens the main menu: player 2
when only his START was pressed, the forty-ninth glue's rule; else player 1) and by po_cmd (the entry of 0x00178AE8: a hero
runs a green command, so a talk, a shop, the Moogle, a save point: the player of that hero), each with the game's counter
(V_OWNSTEP 0x000DE804). po_tick (the field's START look-out, each field step) sets nobody again once the owner is 30 steps old
(what a green command opens comes a few steps later). Only with a twin; one hero: nobody, as before. No fall-back time
(the user: both always play together). Room 0x000DE000 .. 0x000DE200 for the routines and 0x000DE800 .. 0x000DE807 for the
values: 0x000D0000 .. 0x000DEFFF holds no patch word and stayed zero in every run measured (z0, part 137's Gummi runs).
"""
assert t.count(HEADER_OLD) == 1
t = t.replace(HEADER_OLD, HEADER_NEW)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = r'''
# ---- seventy-ninth glue (only with --menuowner) ---------------------------------------------------------------
MO_AT = 0x000DE000                                 # outside the cave: 0x000D0000 .. 0x000DEFFF holds no patch word and
MO_END = 0x000DE200                                # stayed zero in every run measured (z0; part 137's Gummi runs)
V_OWNER = 0x000DE800                               # who owns the screen: 0 nobody (both controllers), 1 player 1, 2 player 2
V_OWNSTEP = 0x000DE804                             # the game's counter (0x0034D4BC) when the owner was set
MO_HOLD = 30                                       # steps the owner outlives the field's START look-out (the screen comes)
MO_SRC = """
po_pad:                           # the second glue's pad_both (0x000F4740) jumps here first. Out: v0 = the record. t2-t7
    lui t7,0x0013
    ori t7,t7,0x8540              # the field's START look-out (the call at 0x00138538) always hears both controllers,
    beq ra,t7,po_both
    lui t7,0x0013
    ori t7,t7,0xC7A0              # and so does the command menu's first button (the call at 0x0013C798)
    beq ra,t7,po_both
    lui t7,0x000E
    lw t6,-6144(t7)               # V_OWNER (0x000DE800)
    beq t6,zero,po_both           # nobody owns the screen: both controllers, as before
    addiu t6,t6,-1                # 0 = player 1, 1 = player 2
    sll t4,t6,6
    sll t3,t6,5
    addu t4,t4,t3                 # times 0x60 (one logical controller record)
    lui t5,0x0035
    addiu t5,t5,-10560            # 0x0034D6C0: logical controller 0
    addu t5,t5,t4                 # the owner's record
    lui v0,0x000F
    addiu v0,v0,0x4800            # pad_both's record (0x000F4800)
    move t2,v0
    addiu t3,t5,0x60
po_copy:                          # the owner's whole record, nothing of the other controller
    ld t4,0(t5)
    sd t4,0(t2)
    addiu t5,t5,8
    bne t5,t3,po_copy
    addiu t2,t2,8
    jr ra
    nop
po_both:
    lui t7,0x0035                 # the two instructions that sat at 0x000F4740
    j 0x000F4748
    addiu t6,t7,-10560

po_open:                          # from 0x00138574 (was jal OPEN_NEXT = mo_open): START opens the main menu. a0, a1 kept
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,poo_go            # one hero: nobody owns menus
    move t3,zero
    lui t5,0x0035
    addiu t5,t5,-10560            # 0x0034D6C0: logical controller 0; controller 1 is 0x60 further
    ld t4,8(t5)                   # pressed, player 1's
    andi t4,t4,0x2
    bne t4,zero,poo_set           # player 1 pressed START (or both did): his menu (the forty-ninth glue's rule)
    addiu t3,zero,1
    ld t4,0x68(t5)                # pressed, player 2's
    andi t4,t4,0x2
    beq t4,zero,poo_set           # nobody pressed START (opened another way): nobody's
    move t3,zero
    addiu t3,zero,2               # only player 2 pressed START: his menu
poo_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter (0x0034D4BC)
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t3,-6144(t7)               # V_OWNER
poo_go:
    j OPEN_NEXT
    nop

po_cmd:                           # the entry of 0x00178AE8 (was j CMD_NEXT = ww_cmd; a0 = a hero): he runs a green command
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,poc_go            # one hero: nobody owns
    addiu t4,zero,1               # player 1's hero: player 1 owns what it opens (a talk, a shop, the Moogle, a save point)
    bne a0,t6,poc_set             # (t4 .. t7 only: t0 .. t3 may carry arguments at a routine's entry)
    nop
    addiu t4,zero,2               # the twin: player 2
poc_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t4,-6144(t7)               # V_OWNER
poc_go:
    j CMD_NEXT
    nop

po_tick:                          # from 0x00138538 (was jal TICK_NEXT): each step the field looks for START
    lui t7,0x000E
    lw t6,-6144(t7)               # V_OWNER
    beq t6,zero,pt_go
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter
    lw t4,-6140(t7)               # V_OWNSTEP
    subu t5,t5,t4
    sltiu t5,t5,MO_HOLD           # set less than MO_HOLD steps ago: what it opens is still coming
    bne t5,zero,pt_go
    nop
    sw zero,-6144(t7)             # the field runs again: nobody owns the screen
pt_go:
    j TICK_NEXT
    nop
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--menuowner" in sys.argv:                                          # seventy-ninth glue (the opener alone controls)
        assert "--ownmenu" in sys.argv and "--ownwallet" in sys.argv, "--menuowner needs --ownmenu (mo_open) and --ownwallet (ww_cmd)"
        tick_next, open_next, cmd_next = words[0x00138538], words[0x00138574], words[0x00178AE8]
        assert (tick_next >> 26) == 3 and (open_next >> 26) == 3 and (cmd_next >> 26) == 2, "the three hooks are not jal / jal / j"
        assert words.get(0x00178AEC) == 0, "the green command's hook has no empty delay slot"
        syms = {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "OPEN_NEXT": (open_next & 0x3FFFFFF) << 2,
                "CMD_NEXT": (cmd_next & 0x3FFFFFF) << 2, "MO_HOLD": MO_HOLD}
        assert V_OWNER == 0x000E0000 - 6144 and V_OWNSTEP == V_OWNER + 4
        code, labels = assemble(MO_AT, MO_SRC, syms)
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert MO_AT + 4 * len(code) <= MO_END, "the seventy-ninth glue does not fit"
        clash = [a for a in words if MO_AT <= a < GQ_TAB]
        assert not clash, "patch words in 0x000DE000 .. 0x000DEFFF: %08X" % clash[0]
        for i, w in enumerate(code):
            a = MO_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (the opener alone controls the screen)"
        hook_base(0x000F4740, 0x3C0F0035, (2 << 26) | ((labels["po_pad"] >> 2) & 0x3FFFFFF), "pad_both: first, does a player own the screen?")
        hook_base(0x000F4744, 0x25EED6C0, 0, "(its delay slot; po_both does the two instructions)")
        hook_base(0x00138538, tick_next, jal(labels["po_tick"]), "the field's START look-out: first, the owner of a closed screen is let go")
        hook_base(0x00138574, open_next, jal(labels["po_open"]), "START opens the main menu: whoever pressed START owns it")
        hook_base(0x00178AE8, cmd_next, (2 << 26) | ((labels["po_cmd"] >> 2) & 0x3FFFFFF), "a hero runs a green command: his player owns what it opens")
        n_glue += len(code)

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the seventy-ninth glue (--menuowner) added")
