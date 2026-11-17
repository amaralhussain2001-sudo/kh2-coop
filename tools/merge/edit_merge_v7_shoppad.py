"""One-off: THE SEVENTIETH GLUE of tools/merge/merge_v7.py (--shoppad): PLAYER 2'S BUTTONS IN THE SHOP'S QUANTITY BOX (ninth round,
STATE part 107; an old fault found while testing the own wallet).
SEEN (runs wa1 on v119 and wa0 on v118 = build 20 without the wallet glue, disc test-s1-hb10s, player 2's hero held at the
item stall, `tests/scripts/own/shop_buy_p2.txt`): player 2's Triangle opens the shop, his Circle closes the information
box and opens Buy and the Potion, but in "Buy how many?" his Circle and Cross do nothing: the box stays to the end.
So in builds up to 20 player 2 cannot finish a purchase.
READ: the shop module (ovl_shop.x at 0x01F18000; its word 0x01F18014 is 0x087C606E) reads the quantity box's buttons in
0x01F1AA70 from the record that the call at 0x01F1AA90 gets: 0x00167F18(0) = logical controller 0 (player 1's) only.
The shop's lists read the menu system that the second glue already gives both controllers.
THE GLUE: sp_inst (the head of the calls at 0x00167E90, the controller task, every frame): while the shop module is in
memory and its call at 0x01F1AA90 is still the game's (jal 0x00167F18), it becomes jal 0x000F4740 = the second glue's
pad_both (a record with the buttons of both controllers, OR-ed; the stick of player 1 or, at rest, of player 2), as
for the text boxes. Code at 0x000EDB00 (the sixty-ninth glue's range ends there now).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_shoppad.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--shoppad" in s:
    raise SystemExit("already there")

DOC = '''SEVENTIETH GLUE (built only with the option --shoppad): PLAYER 2'S BUTTONS IN THE SHOP'S QUANTITY BOX. The shop module reads
"Buy how many?" from logical controller 0 only (its call at 0x01F1AA90), so player 2 could not finish a purchase. sp_inst
(head of the controller task's calls at 0x00167E90) points that call at the second glue's pad_both (both controllers)
whenever the shop module is in memory.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

old = "WW_END = 0x000EDC00\n"
assert s.count(old) == 1
s = s.replace(old, "WW_END = 0x000EDB00                                # (0x000EDB00 .. 0x000EDC00: the seventieth glue)\n")

SRC = '''# ---- seventieth glue (only with --shoppad) ------------------------------------------------------------------
SPP_AT = 0x000EDB00
SPP_END = 0x000EDC00
SPP_SRC = """
sp_inst:                          # from 0x00167E90 (the controller task, every frame): first, the shop module's getter call
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which module is in memory (0x606E = the shop)
    ori t5,zero,0x606E
    bne t6,t5,spi_go
    nop
    lw t4,-21872(t7)              # 0x01F1AA90: still the game's call (jal 0x00167F18: logical controller 0 only)?
    lui t3,0x0C05
    ori t3,t3,0x9FC6
    bne t4,t3,spi_go
    lui t3,0x0C03
    ori t3,t3,0xD1D0              # jal 0x000F4740: the second glue's pad_both (both controllers)
    sw t3,-21872(t7)
spi_go:
    j SPP_NEXT
    nop
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--shoppad" in sys.argv:                                            # seventieth glue (player 2's buttons in the shop's quantity box)
        spp_next = words[0x00167E90]
        assert (spp_next >> 26) == 3
        assert words.get(0x000F4740) is not None, "--shoppad needs the second glue's pad_both at 0x000F4740"
        labels, n = add_code(SPP_AT, SPP_END, SPP_SRC, {"SPP_NEXT": (spp_next & 0x3FFFFFF) << 2},
                             "player 2's buttons in the shop's quantity box")
        hook_base(0x00167E90, spp_next, jal(labels["sp_inst"]), "the controller task: first, the shop module's quantity box listens to both controllers")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
