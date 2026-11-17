"""One-off: tools/merge/merge_v7.py gets the FORTY-EIGHTH GLUE, built only with the option --ownrec (plan row 39,
stage 1, step 1): THE SECOND HERO'S UNIT SLOT READS A CHARACTER RECORD OF HIS OWN.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownrec.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "t_load" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-EIGHTH GLUE (NOT in builds 13 / 14; built only with the option --ownrec): THE SECOND HERO'S UNIT SLOT READS A
CHARACTER RECORD OF HIS OWN (plan row 39 "own gear for each player", stage 1, step 1; job 11 of the eighth round).
What is there (lane D, `tools/lane-d/make_ownhp2.py`): both heroes' unit slots point at the SAME character record
(Sora's, save + 0x24F0 = 0x0032E020, 0x114 bytes; slot + 0x244); only the current HP / MP bytes are the twin's own.
The game loads a slot's stats, abilities and equipment bonuses from that record in 0x001A11E0(slot, record or 0)
(experiments e1a / e1b / e1c: a second record in the twin's slot works).
Now t_load (the jump at 0x001A1200, the routine's "which record" step): for the twin's slot (lane D's mark, bit 31
of slot + 0x250) the record is T (0x000E7D00, 0x114 bytes; 0x000E7E20 = the record T was made from):
 - the first time, or when the source record is another one (Sora -> Roxas ...): T = a full copy of the source;
 - every later time: the COMMON parts are copied from the source again (+ 2 .. + 0x13: HP / MP, AP, the three
   bonuses, the level, the counts of places; + 0x34 .. + 0x53: the item places, common in this stage), and the
   ability list (+ 0x54 .. + 0x113): where the same ability stands in both lists the twin's own "switched on"
   bit stays, anything else is taken from the source as it is;
 - THE TWIN'S OWN: + 0 the Keyblade, + 0x14 .. + 0x33 the armour and accessory places, the "switched on" bits.
 - the slot's pointer (slot + 0x244) is set to T.
With this glue ALONE nothing can change the twin's own parts yet (they stay what they were at the first copy).

'''
s = s.replace(a, hdr + a)
b = "[--playernear] [--no-sender]"
assert s.count(b) == 1
s = s.replace(b, b + " [--ownrec]")
i = s.index("def main():")
src = '''# ---- forty-eighth glue (only with --ownrec) ----------------------------------------------------------------
RT_AT = 0x000E9800
RT_END = 0x000E9A00
REC_T = 0x000E7D00                                 # the twin's own character record (0x114 bytes)
V_TSRC = 0x000E7E20                                # the record T was made from (0 = not made yet)
RT_SRC = """
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
    ori t6,t6,0x7D00              # record T
    lui t5,0x000E
    bne a1,zero,tl_s1
    lw t4,0x7E20(t5)              # the record T was made from
    lw a1,0x244(a0)               # no record given: the slot's own
    beq a1,zero,tl_game           # none: as the game
    nop
tl_s1:
    bne a1,t6,tl_s2
    nop
    move a1,t4                    # the slot's record is T already: the source is the remembered one
    beq a1,zero,tl_use            # (cannot be) T without a source: use it as it is
    nop
tl_s2:
    beq a1,t4,tl_ref
    nop
    sw a1,0x7E20(t5)              # a new source (the first time, or another character): T = all of it
    addiu t3,zero,0x114
    move t2,a1
    move t1,t6
tl_cp:
    lw t0,0(t2)
    sw t0,0(t1)
    addiu t3,t3,-4
    addiu t2,t2,4
    bgtz t3,tl_cp
    addiu t1,t1,4
    b tl_use
    nop
tl_ref:                           # the common parts again
    lhu t0,2(a1)
    sh t0,2(t6)
    lw t0,4(a1)
    sw t0,4(t6)
    lw t0,8(a1)
    sw t0,8(t6)
    lw t0,12(a1)
    sw t0,12(t6)
    lw t0,16(a1)
    sw t0,16(t6)
    addiu t2,a1,0x34              # the item places: common in this stage
    addiu t1,t6,0x34
    addiu t3,zero,0x20
tl_it:
    lw t0,0(t2)
    sw t0,0(t1)
    addiu t3,t3,-4
    addiu t2,t2,4
    bgtz t3,tl_it
    addiu t1,t1,4
    addiu t3,zero,0xC0            # the abilities (t2 / t1 stand at + 0x54 now)
tl_ab:
    lhu t0,0(t2)
    lhu t9,0(t1)
    xor t8,t0,t9
    andi t8,t8,0x7FFF
    beq t8,zero,tl_ab2            # the same ability stands there: the twin's own "switched on" bit stays
    addiu t3,t3,-2
    sh t0,0(t1)                   # another one (a new ability, a new order): the source's entry as it is
tl_ab2:
    addiu t2,t2,2
    bgtz t3,tl_ab
    addiu t1,t1,2
tl_use:
    sw t6,0x244(a0)               # the twin's slot reads his own record
    j 0x001A1214
    daddu s1,t6,zero
"""
RT_HOOK = (0x001A1200, 0x14A00004, 0x00A0882D)     # bne a1,zero,0x001A1214 / daddu s1,a1,zero


'''
s = s[:i] + src + s[i:]
e = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(e) == 1
step = '''    if "--ownrec" in sys.argv:                                             # forty-eighth glue (plan row 39; not in builds 13 / 14)
        labels, n = add_code(RT_AT, RT_END, RT_SRC, {}, "the second hero's unit slot reads a character record of his own")
        a, w0, w1 = RT_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["t_load"] >> 2) & 0x3FFFFFF), "load a slot's stats: which record (the twin's own record T)")
        hook_game(a + 4, w1, 0, "(daddu s1,a1,zero is done in t_load)")
        n_glue += n + 2

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
