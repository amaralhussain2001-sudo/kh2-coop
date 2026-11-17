"""One-off: tools/merge/merge_v7.py gets the SIXTY-FIRST GLUE (built only with --itemsync, with --ownrec --norec):
PLAYER 2'S ITEM LIST SHOWS THE ITEM PLACES AS THEY ARE.
What was there (eighth round, part 85; runs it3, it5 on build 18's patch; the fault is in every build since 15):
the item places are common (Sora's record + 0x34). When PLAYER 2 uses an item from his command menu the game takes
it out of Sora's record, which is right; but his "Items" list is built from the twin's view T (glue 48: a copy
made at his stat load), and T is not made anew after his own use. Run it5: three Potions; after he used all
three Sora's places are empty, T still holds three, and his list says "Potion x3"
(`local\\tests\\r8it5-HB13_ROAM-0\\p2_f006330.png`): he can take a Potion that is not there.
gi_sync (the jump at 0x001BE9DC, in front of the fifty-third glue's gn_cnt; the list builder 0x001BE9A0 has just
asked for the hero's record, v0): when that record is the view T, T's item places and the eight words behind them
(+ 0x34 .. + 0x53) are copied from the record T shows, first.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_itemsync.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gi_sync" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTY-FIRST GLUE (built only with the option --itemsync, with --ownrec --norec): PLAYER 2'S ITEM LIST SHOWS THE
ITEM PLACES AS THEY ARE. The item places are common (Sora's record); the game takes a used item out of Sora's
record also when player 2 used it, but his list is built from the view T, a copy that was not made anew: his
list kept items that were gone. gi_sync (the jump at 0x001BE9DC, in front of gn_cnt): when the list builder's
record is the view T, T's + 0x34 .. + 0x53 are copied from the record T shows, first.

'''
s = s.replace(a, hdr + a)
b = " [--holdwatch]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--itemsync]")

i = s.index("def main():")
src = '''# ---- sixty-first glue (only with --itemsync) ----------------------------------------------------------------
GI_AT = 0x000EC100
GI_END = 0x000EC140
GI_SRC = """
gi_sync:                          # jump at 0x001BE9DC, in front of gn_cnt. v0 = the record the item list is built from
    lui t7,0x000E
    ori t6,t7,0x7D00              # the twin's view T
    bne v0,t6,gi_go
    lw t5,0x7E20(t7)              # the record T shows
    beq t5,zero,gi_go
    addiu t4,zero,8               # eight words: the item places and the eight words behind them (+ 0x34 .. + 0x53)
gi_l:
    lw t3,0x34(t5)
    sw t3,0x34(t6)
    addiu t4,t4,-1
    addiu t5,t5,4
    bgtz t4,gi_l
    addiu t6,t6,4
gi_go:
    j GN_CNT
    nop
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--itemsync" in sys.argv:                                           # sixty-first glue (player 2's item list shows the places as they are)
        gn_next = words.get(0x001BE9DC)
        assert "--ownrec" in sys.argv and gn_next is not None and (gn_next >> 26) == 2, "--itemsync needs --ownrec and --norec (the jump at 0x001BE9DC)"
        labels, n = add_code(GI_AT, GI_END, GI_SRC, {"GN_CNT": (gn_next & 0x3FFFFFF) << 2},
                             "player 2's item list is built from the item places as they are")
        hook_base(0x001BE9DC, gn_next, (2 << 26) | ((labels["gi_sync"] >> 2) & 0x3FFFFFF), "the command menu counts the hero's item places: first, the view's places are made fresh")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
