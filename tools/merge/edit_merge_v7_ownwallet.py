"""One-off: THE SIXTY-NINTH GLUE of tools/merge/merge_v7.py (--ownwallet, with --ownkey): PLAYER 2'S OWN WALLET (ninth round,
the user's answer D of 2026-11-15: "each player his own bag and wallet; the money they gain goes to both; while they spend
it each one alone"; STATE parts 105, 107).
READ (STATE part 107): the wallet is save + 0x2440 (0x0032DF70); munny is added only by 0x00242500 (callers: the script
call 0x001750E8 = rewards, the munny orb 0x001A5364 = a pickup, the shop module's sale at 0x01F1B268) and paid only by
0x00242590 (the shop module's purchase at 0x01F1B1EC). A shop (and the Moogle) is the game mode whose record lies at
0x0033CB80 (written at boot by 0x00105D50): its start routine (+ 0x20) is 0x00105C68, which loads ovl_shop.x. A hero
runs a green command through the method 0x00178AE8 (a0 = the hero; table word 0x0034E9F0 and three direct calls).
THE GLUE:
  ww_cmd   (the entry of 0x00178AE8): the hero who runs a command and the game's counter are noted (0x000E7FA0 / A4).
  ww_sstart (the shop mode's start, the word at 0x0033CBA0): the shop is player 2's when the last command was run by
           the twin less than 600 steps ago; then his menu things go in exactly as for his pause menu (glue 49's flag
           0x000E7E24 = 1, ow_swap with its chain: armour, accessories, ability switches, item places, stock,
           shortcuts, Keyblade and now the wallet; ow_load). Glue 49's ms_tick puts them back at the field's next step,
           as after his pause menu. 0x000E7FA8 = whose shop (1 / 2).
  ww_swap  (chained after glue 63's kb_swap): the two wallets change places.
  ww_add   (the entry of 0x00242500): MUNNY THE GAME GIVES GOES TO BOTH: player 2's wallet gets the same amount (up to
           999,999), unless a shop is open (a sale is the seller's alone) or his menu things are in.
  ww_tick  (each step of the field): no shop is open any more; no mark yet: player 2's wallet = player 1's.
PLAYER 2'S WALLET: King Mickey's record + 0x48 (0x0032E3A4, 4 bytes), its mark 0x5035 at + 0x4C (read-proven free bytes,
part 89; + 0x46 is glue 63's mark). The glue 65's range ends at 0x000ED900 now (its code ends at 0x000ED8E0); this glue
lives at 0x000ED900 .. 0x000EDC00.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownwallet.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--ownwallet" in s:
    raise SystemExit("already there")

DOC = '''SIXTY-NINTH GLUE (built only with the option --ownwallet, with --ownkey): PLAYER 2'S OWN WALLET. His munny is a word in
King Mickey's record (0x0032E35C + 0x48, the mark 0x5035 at + 0x4C). Munny the game gives (0x00242500: rewards, orbs) goes
to both wallets; a shop's sale is the seller's alone. A shop or the Moogle (the game mode at 0x0033CB80, start 0x00105C68)
is player 2's when the twin ran the last green command (0x00178AE8): then his menu things go in as for his pause menu
(glue 49's flag and ow_swap chain; the wallets change places at its end), so he pays from his own wallet.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

old = "HP_END = 0x000EDC00\n"
assert s.count(old) == 1
s = s.replace(old, "HP_END = 0x000ED900                                # (its code ends at 0x000ED8E0; 0x000ED900 .. 0x000EDC00 is the sixty-ninth glue's)\n")

SRC = '''# ---- sixty-ninth glue (only with --ownwallet) ----------------------------------------------------------------
WW_AT = 0x000ED900
WW_END = 0x000EDC00
WW_P2 = 0x0032E3A4 - 0x00330000                    # player 2's wallet: King Mickey's record + 0x48
WW_MARK = 0x0032E3A8 - 0x00330000                  # its mark 0x5035: King Mickey's record + 0x4C
WW_SRC = """
ww_cmd:                           # the entry of 0x00178AE8 (a0 = a hero): he runs a green command
    lui t7,0x000E
    sw a0,0x7FA0(t7)              # the hero
    lui t6,0x0035
    lw t6,-11076(t6)              # the game's counter (0x0034D4BC)
    sw t6,0x7FA4(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x00178AE8
    j 0x00178AF0
    addiu t7,zero,32

ww_sstart:                        # the shop mode's start (the word at 0x0033CBA0; was 0x00105C68), a0 = the shop
    lui t7,0x000E
    addiu t0,zero,1               # player 1's shop, unless:
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,wss_set
    lw t5,0x7FA0(t7)              # the twin ran the last green command,
    bne t5,t6,wss_set
    lui t4,0x0035
    lw t4,-11076(t4)
    lw t3,0x7FA4(t7)
    subu t4,t4,t3
    sltiu t4,t4,600               # less than 600 steps ago,
    beq t4,zero,wss_set
    lw t2,0x7E24(t7)              # his menu things are not in already,
    bne t2,zero,wss_set
    lw t2,0x7E28(t7)              # and the hero's record is noted
    beq t2,zero,wss_set
    nop
    addiu t0,zero,2
wss_set:
    sw t0,0x7FA8(t7)              # whose shop
    addiu t1,zero,2
    bne t0,t1,wss_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    addiu t1,zero,1
    sw t1,0x7E24(t7)              # his menu things go in (glue 49's ms_tick puts them back at the field's next step)
    jal OW_SWAP
    nop
    jal OW_LOAD
    nop
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
wss_go:
    j 0x00105C68
    nop

ww_swap:                          # the end of glue 63's kb_swap (was jr ra): player 2's menu things go in or out
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    beq t5,t4,wsw_do
    lw t3,-8336(t6)               # player 1's wallet (0x0032DF70)
    sw t3,@WW@(t6)                # (no mark yet: his wallet = player 1's)
    sh t4,@WM@(t6)
wsw_do:
    lw t3,-8336(t6)
    lw t2,@WW@(t6)
    sw t2,-8336(t6)               # the two wallets change places
    jr ra
    sw t3,@WW@(t6)

ww_add:                           # the entry of 0x00242500 (a0 = munny): the game gives munny
    lui t7,0x000E
    lw t6,0x7FA8(t7)
    bne t6,zero,wa_go             # a shop is open: a sale is the seller's alone
    lw t6,0x7E24(t7)
    bne t6,zero,wa_go             # (his menu things are in: as the game)
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    bne t5,t4,wa_go               # (no wallet yet: the tick makes it = player 1's, this munny included)
    lw t3,@WW@(t6)
    addu t3,t3,a0                 # MUNNY THE GAME GIVES GOES TO BOTH
    lui t2,0x000F
    ori t2,t2,0x423F              # 999,999
    sltu t1,t2,t3
    movn t3,t2,t1
    sw t3,@WW@(t6)
wa_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x00242500
    j 0x00242508
    sd s0,0(sp)

ww_tick:                          # from 0x00138538 (each step of the field)
    lui t7,0x000E
    sw zero,0x7FA8(t7)            # the field runs: no shop is open
    lw t6,0x7E24(t7)
    bne t6,zero,wt_go             # (his menu things are in: not now)
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    beq t5,t4,wt_go
    lw t3,-8336(t6)
    sw t3,@WW@(t6)                # no mark yet (a new game, an older save): his wallet = player 1's
    sh t4,@WM@(t6)
wt_go:
    j TICK_NEXT
    nop
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--ownwallet" in sys.argv:                                          # sixty-ninth glue (player 2's own wallet)
        assert "--ownkey" in sys.argv and "--ownmenu" in sys.argv, "--ownwallet needs --ownkey (its swap chain) and --ownmenu"
        _c, rm_l = assemble(RM_AT, RM_SRC, {})
        _c, kb_l = assemble(KB_AT, KB_SRC, {"TICK_NEXT": 0, "WC_BOTH": WC_AT})
        kw = kb_l["kw_out"]
        assert words.get(kw) == 0x03E00008, "kb_swap's end is not jr ra: %s" % words.get(kw)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        src = WW_SRC.replace("@WW@", str(WW_P2)).replace("@WM@", str(WW_MARK))
        labels, n = add_code(WW_AT, WW_END, src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "OW_SWAP": rm_l["ow_swap"],
                                                  "OW_LOAD": rm_l["ow_load"]}, "player 2's own wallet")

        def jw(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["ww_tick"]), "the field's START look-out: first, player 2's wallet is made, no shop is open")
        hook_base(kw, 0x03E00008, jw(labels["ww_swap"]), "player 2's menu things go in or out: the wallets change places")
        hook_game(0x00178AE8, 0x27BDFFF0, jw(labels["ww_cmd"]), "a hero runs a green command: he is noted")
        hook_game(0x00178AEC, 0x240F0020, 0, "(its delay slot)")
        hook_game(0x00242500, 0x27BDFFF0, jw(labels["ww_add"]), "the game gives munny: to both wallets")
        hook_game(0x00242504, 0xFFB00000, 0, "(its delay slot)")
        assert 0x0033CBA0 not in words
        words[0x0033CBA0] = labels["ww_sstart"]                            # the shop mode's start (a data word the game writes at boot)
        order.append(0x0033CBA0)
        origin[0x0033CBA0] = "glue 8 hook: the shop mode's start: whose shop is it (was 0x00105C68)"
        n_glue += n + 5

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
