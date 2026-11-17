"""One-off: THE SEVENTY-FIRST GLUE of tools/merge/merge_v7.py (--ownbag, with --ownwallet): PLAYER 2'S OWN BAG (ninth round, the
user's answer D of 2026-11-15: "each player his own bag and wallet"; STATE parts 105, 107, 108).
WHAT IS HIS OWN: the counts of the 158 things a player keeps and chooses: 31 Keyblades, 34 armours, 33 accessories, 60
materials (item types 2, 14, 15, 16 of the item table, 03system.bin). The fight items had their own stock since
glue 62. STILL COMMON (said in the read-me): Tent, the Boosts and the Drive recoveries (they act on the one Sora
record and the party), Donald's, Goofy's and the guests' weapons, the recipes, Torn Pages, the magic elements, key items.
WHERE: King Mickey's ability list, places 16 .. 79 (0x0032E3D0 .. 0x0032E44F). READ (part 108): the game clears a record's
ability list only in the New Game init (0x001888C8 from 0x00188E08) and in the Continue snapshot's own init; an ability
is added into the FIRST EMPTY place (King Mickey gets two; places 0 .. 15 stay his); the stats loader (0x001C3060)
skips every entry whose bit 15 is clear before it looks anything up; the count of an ability (0x001A35F8) compares
(entry & 0x7FFF) with an item id (< 0x4000). So every place here keeps bit 15 clear and bit 14 set (0x4000 | 14 bits)
and is never 0: place k (0 .. 63): its low byte = material k's count (k < 60; 0 .. 99), its high byte = 0x40 | A << 3 | B
with A, B = the counts of the gear numbers 2k and 2k + 1 (0 .. 7: PLAYER 2'S BAG KEEPS UP TO 7 OF ONE KEYBLADE, ARMOUR
OR ACCESSORY). The mark 0x5036 at King Mickey's record + 0x4E. The table ob_tab (built from the item table) gives
each of the 158 numbers its place in the game's bag (save + 0x3580).
HOW: ob_swap (after the sixty-ninth glue's ww_swap, in glue 49's swap chain, so for his pause menu AND his shop / the
Moogle): IN: player 1's 158 counts go to a buffer (0x000E7C40), player 2's counts into the game's bag; OUT: the bag's
counts become player 2's again, player 1's come back (0x000E7FAC = his bag is in). ob_gain (glue 62's og_eq: what
the game gives that is not a fight item): a Keyblade, an armour, an accessory or a material goes into the game's bag
AND into player 2's (while his bag is in: into player 1's buffer); glue 62's "gear twice into the one bag" is not
made any more. ob_tick (the field's step): no mark yet (a new game, an older save): his bag = player 1's.
The code: 0x000EE260 (glue 66's range ends there now), 0x000EB300 (glue 51's), 0x000E9900 (glue 48's), the table at
0x000EE6C0.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownbag.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--ownbag" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-FIRST GLUE (built only with the option --ownbag, with --ownwallet): PLAYER 2'S OWN BAG. His counts of the Keyblades,
armours, accessories and materials (158 things) live in King Mickey's ability places 16 .. 79 (0x4000 | 14 bits each: a
material's count in the low byte, two gear counts of 3 bits in the high byte; the mark 0x5036 at + 0x4E). ob_swap
(after ww_swap) puts them into the game's bag while his menu or his shop is open (player 1's wait in 0x000E7C40);
ob_gain gives a thing the game gives into both bags; ob_tick makes his bag = player 1's when there is no mark.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

for old, new in (("RT_END = 0x000E9A00\n", "RT_END = 0x000E9900                                # (0x000E9900 .. 0x000E9A00: the seventy-first glue's ob_gain)\n"),
                 ("GS_END = 0x000EB400\n", "GS_END = 0x000EB300                                # (0x000EB300 .. 0x000EB400: the seventy-first glue's ob_tick)\n"),
                 ("GQ_END = 0x000EE400\n", "GQ_END = 0x000EE260                                # (0x000EE260 .. 0x000EE400: the seventy-first glue's swap)\n")):
    assert s.count(old) == 1, old
    s = s.replace(old, new)

# glue 62's og_eq: with --ownbag the first instruction jumps to ob_gain (same size: no label moves)
old = '''og_eq:
    beq t2,t3,og_two              # a Keyblade
    addiu t3,zero,14
'''
assert s.count(old) == 1
a = '''GO_SRC = """'''
assert s.count(a) == 1
i = s.index(a)
j = s.index(NL + '"""', i + len(a)) + 1         # the closing line of the source
j = s.index(NL, j) + 1                          # the line after it
while s[j:].startswith("   .replace("):         # (the statement goes on in .replace lines)
    j = s.index(NL, j) + 1
s = s[:j] + '''
if "--ownbag" in sys.argv:                         # (the seventy-first glue: what the game gives goes into both own bags)
    GO_SRC = GO_SRC.replace("""og_eq:
    beq t2,t3,og_two              # a Keyblade
""", """og_eq:
    j 0x000E9900                  # (--ownbag) a thing that is not a fight item: the seventy-first glue's ob_gain
""")
''' + s[j:]

SRC = '''# ---- seventy-first glue (only with --ownbag) -----------------------------------------------------------------
OB_A_AT = 0x000EE260                               # ob_get, ob_put, ob_swap
OB_A_END = 0x000EE400
OB_T_AT = 0x000EE6C0                               # ob_tab: the 158 bag places (halfwords)
OB_T_END = 0x000EE800
OB_B_AT = 0x000EB300                               # ob_tick
OB_B_END = 0x000EB400
OB_C_AT = 0x000E9900                               # ob_gain (glue 62's og_eq jumps here)
OB_C_END = 0x000E9A00
OB_P2 = 0x0032E3D0 - 0x00330000                    # player 2's bag: King Mickey's ability places 16 .. 79
OB_MARK = 0x0032E3AA - 0x00330000                  # its mark 0x5036: King Mickey's record + 0x4E
OB_BAG = 0x0032F0B0 - 0x00330000                   # the game's bag (save + 0x3580)


def ob_table():
    """The 158 bag places: the 60 materials (type 16), then the Keyblades (2), armours (14), accessories (15), each by id."""
    d = (ROOT / "local" / "extract" / "kh2" / "03system.bin").read_bytes()
    cnt = struct.unpack_from("<I", d, 4)[0]
    for i in range(cnt):
        _typ, name, off, _size = struct.unpack_from("<I4sII", d, 16 + 16 * i)
        if name.rstrip(b"\\0") == b"item":
            break
    else:
        raise SystemExit("03system.bin has no item table")
    _ver, n = struct.unpack_from("<II", d, off)
    by = {}
    for k in range(n):
        e = struct.unpack_from("<HBBBBHHHHHHHHBB", d, off + 8 + 24 * k)
        by.setdefault(e[1], []).append((e[0], e[11]))
    places = [pl for t in (16, 2, 14, 15) for _iid, pl in sorted(by[t])]
    assert len(places) == 158 and len(set(places)) == 158 and max(places) < 0x138, (len(places), len(set(places)))
    return places


OB_A_SRC = """
ob_get:                           # a0 = a number (0 .. 157): v0 = player 2's count of it
    sltiu t0,a0,60
    beq t0,zero,obg_g
    lui t1,0x0033
    sll t0,a0,1
    addu t0,t0,t1
    jr ra
    lbu v0,@P2@(t0)               # a material: the low byte of place a0
obg_g:
    addiu t0,a0,-60               # gear number g: place g / 2, its high byte
    srl v0,t0,1
    sll v0,v0,1
    addu v0,v0,t1
    lbu v0,@P2H@(v0)
    andi t0,t0,1
    bne t0,zero,obg_lo
    nop
    srl v0,v0,3
obg_lo:
    jr ra
    andi v0,v0,7

ob_put:                           # a0 = a number, a1 = player 2's count of it (made 0 .. 99 / 0 .. 7)
    sltiu t0,a0,60
    beq t0,zero,obp_g
    lui t1,0x0033
    sltiu t0,a1,100
    bne t0,zero,obp_m
    nop
    addiu a1,zero,99
obp_m:
    sll t0,a0,1
    addu t0,t0,t1
    jr ra
    sb a1,@P2@(t0)
obp_g:
    sltiu t0,a1,8
    bne t0,zero,obp_g1
    nop
    addiu a1,zero,7
obp_g1:
    addiu t0,a0,-60
    srl t2,t0,1
    sll t2,t2,1
    addu t2,t2,t1
    lbu t3,@P2H@(t2)              # 0x40 | A << 3 | B
    andi t0,t0,1
    bne t0,zero,obp_b
    nop
    andi t3,t3,0x47               # A is this one
    sll a1,a1,3
    b obp_w
    or t3,t3,a1
obp_b:
    andi t3,t3,0x78               # B is this one
    or t3,t3,a1
obp_w:
    ori t3,t3,0x40
    jr ra
    sb t3,@P2H@(t2)

ob_swap:                          # the end of the sixty-ninth glue's ww_swap (was jr ra): player 2's menu things go in or out
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    bne t8,t7,obs_ret             # no own bag yet
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    move s0,zero                  # the number
obs_l:
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    sll t5,s0,1
    addu t6,t6,t5
    lhu s1,0(t6)                  # its place in the bag
    lui t6,0x0033
    addu s1,s1,t6                 # (its count: @BAG@(s1))
    lui t5,0x000E
    lw t7,0x7FAC(t5)
    bne t7,zero,obs_o
    addu t4,t5,s0
    lbu t3,@BAG@(s1)              # IN: player 1's count waits in the buffer,
    sb t3,0x7C40(t4)
    jal ob_get
    move a0,s0
    b obs_n
    sb v0,@BAG@(s1)               # player 2's count is in the bag
obs_o:
    lbu a1,@BAG@(s1)              # OUT: the bag's count is player 2's,
    jal ob_put
    move a0,s0
    lui t5,0x000E
    addu t4,t5,s0
    lbu t3,0x7C40(t4)
    sb t3,@BAG@(s1)               # player 1's comes back
obs_n:
    addiu s0,s0,1
    sltiu t0,s0,158
    bne t0,zero,obs_l
    nop
    lui t5,0x000E
    lw t7,0x7FAC(t5)
    xori t7,t7,1
    sw t7,0x7FAC(t5)              # in <-> out
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    addiu sp,sp,32
obs_ret:
    jr ra
    nop
"""

OB_B_SRC = """
ob_tick:                          # from 0x00138538 (the field's step): no own bag yet: his bag = player 1's
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    beq t8,t7,obt_go
    lui t6,0x000E
    lw t6,0x7E24(t6)              # (his menu things are in: not now)
    bne t6,zero,obt_go
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    addiu t0,zero,64              # the 64 places: 0x4000 = nothing
    addiu t1,t9,@P2@
    ori t2,zero,0x4000
obt_c:
    sh t2,0(t1)
    addiu t0,t0,-1
    bne t0,zero,obt_c
    addiu t1,t1,2
    move s0,zero
obt_l:
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    sll t5,s0,1
    addu t6,t6,t5
    lhu s1,0(t6)
    lui t6,0x0033
    addu s1,s1,t6
    lbu a1,@BAG@(s1)
    jal OB_PUT
    move a0,s0
    addiu s0,s0,1
    sltiu t0,s0,158
    bne t0,zero,obt_l
    nop
    lui t9,0x0033
    addiu t7,zero,0x5036
    sh t7,@MK@(t9)
    lui t6,0x000E
    sw zero,0x7FAC(t6)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    addiu sp,sp,32
obt_go:
    j TICK_NEXT
    nop
"""

OB_C_SRC = """
ob_gain:                          # from glue 62's og_eq (t2 = the type, a0 = the item, a1 = the count, s2 = its table entry): THE GAME GIVES IT
    addiu t3,zero,2
    beq t2,t3,obn_y               # a Keyblade
    addiu t3,zero,14
    beq t2,t3,obn_y               # an armour
    addiu t3,zero,15
    beq t2,t3,obn_y               # an accessory
    addiu t3,zero,16
    bne t2,t3,obn_go              # (not a material either: as the game)
    nop
obn_y:
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    bne t8,t7,obn_go              # no own bag yet
    nop
    lhu t4,0x12(s2)               # its place in the bag
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    move t5,zero
obn_f:
    lhu t7,0(t6)
    beq t7,t4,obn_s
    nop
    addiu t5,t5,1
    sltiu t7,t5,158
    bne t7,zero,obn_f
    addiu t6,t6,2
    b obn_go                      # (not in the list)
    nop
obn_s:
    lui t7,0x000E
    lw t7,0x7FAC(t7)
    beq t7,zero,obn_p2
    nop
    lui t7,0x000E                 # his bag is in: the game's add is his; player 1's count waits in the buffer
    addu t7,t7,t5
    lbu t6,0x7C40(t7)
    addu t6,t6,a1
    sltiu t8,t6,100
    bne t8,zero,obn_b
    nop
    addiu t6,zero,99
obn_b:
    b obn_go
    sb t6,0x7C40(t7)
obn_p2:
    addiu sp,sp,-32               # player 1's bag gets it from the game, player 2's the same here
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd t5,24(sp)
    jal OB_GET
    move a0,t5
    ld a1,16(sp)
    ld a0,24(sp)
    jal OB_PUT
    addu a1,a1,v0
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
obn_go:
    j 0x001A32C8                  # the game's add to the bag
    nop
"""


def ob_src(src):
    return (src.replace("@P2H@", str(OB_P2 + 1)).replace("@P2@", str(OB_P2)).replace("@MK@", str(OB_MARK))
            .replace("@BAG@", str(OB_BAG)))

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--ownbag" in sys.argv:                                             # seventy-first glue (player 2's own bag)
        assert "--ownwallet" in sys.argv, "--ownbag needs --ownwallet (its swap ends the chain)"
        places = ob_table()
        tab = [".word 0x%08X" % (places[i] | ((places[i + 1] if i + 1 < len(places) else 0) << 16)) for i in range(0, len(places), 2)]
        _t, n_t = add_code(OB_T_AT, OB_T_END, "ob_tab:\\n" + "\\n".join("    " + x for x in tab) + "\\n", {}, "player 2's own bag: the 158 places")
        oa, n_a = add_code(OB_A_AT, OB_A_END, ob_src(OB_A_SRC), {"OB_TAB": OB_T_AT}, "player 2's own bag: his counts, the swap")
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _ob, n_b = add_code(OB_B_AT, OB_B_END, ob_src(OB_B_SRC), {"OB_TAB": OB_T_AT, "OB_PUT": oa["ob_put"], "TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                            "player 2's own bag: made = player 1's when there is no mark")
        oc, n_c = add_code(OB_C_AT, OB_C_END, ob_src(OB_C_SRC), {"OB_TAB": OB_T_AT, "OB_GET": oa["ob_get"], "OB_PUT": oa["ob_put"]},
                           "player 2's own bag: what the game gives goes into both bags")
        assert oc["ob_gain"] == 0x000E9900, "glue 62's og_eq jumps to 0x000E9900"
        _c, ww_l = assemble(WW_AT, WW_SRC.replace("@WW@", str(WW_P2)).replace("@WM@", str(WW_MARK)),
                            {"TICK_NEXT": 0, "OW_SWAP": 0, "OW_LOAD": 0})
        wj = ww_l["ww_add"] - 8                                            # ww_swap's jr ra (its delay slot is the last store)
        assert words.get(wj) == 0x03E00008, "ww_swap's end is not jr ra"
        hook_base(wj, 0x03E00008, (2 << 26) | ((oa["ob_swap"] >> 2) & 0x3FFFFFF), "player 2's menu things go in or out: the bags too")
        hook_base(0x00138538, tick_next, jal(_ob["ob_tick"]), "the field's START look-out: first, player 2's own bag is made")
        n_glue += n_t + n_a + n_b + n_c

'''
a = '''    if "--shoppad" in sys.argv:                                            # seventieth glue'''
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
