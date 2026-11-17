"""One-off: tools/merge/merge_v7.py gets the FIFTY-NINTH GLUE (built only with --onevictim, with --together):
A BOSS THAT HOLDS ONE HERO MAKES ITS FURTHER CAPTURES ON THAT HERO.
What was there (eighth round, part 81; run r9hb lk15 59, the Groundshaker, candidate v89, both players Circle /
Triangle / R1, HP held): player 2's hero was in the boss's ride (captured motions FC / FD / FE ...). At frame 8650
the script's next capture (FE) went onto PLAYER 1's hero, who was free; player 2's sequence went on and ended
(FF at 8896), but nobody ever let player 1's hero go: he stood in action FE at one place for the last 11,250
frames of the run. Read: the script keeps the capture it made in ITS OWN work memory (work + 132 / 128 / 124,
`local\\analysis\\h\\ai\\B_LK120.txt` L3906) and is written for one hero; which hero a capture lands on is asked
anew at each step. (At Scar, run r9ha lk14 55, the same split was seen; there both happened to end.)
gk_cap (the jump at 0x00180378, in front of the fiftieth glue's tg_cap): the victim is a hero who is NOT held,
  the other hero IS held (action FC .. FF) by this same captor (hero + 0x240 = the captor's word): the capture
  is made on the held hero. Not in Shan-Yu's room (world 08 room 09), where the fiftieth glue makes pairs.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_onevictim.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gk_cap" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-NINTH GLUE (built only with the option --onevictim, with --together): A BOSS THAT HOLDS ONE HERO MAKES
ITS FURTHER CAPTURES ON THAT HERO. A boss's script is written for one hero and keeps "the capture I made" in its
own work memory; with two heroes one step of a sequence could land on the free hero, who was then never let go
(the Groundshaker, lk15: a hero in action FE for 11,250 frames). gk_cap (the jump at 0x00180378, in front of
tg_cap): the victim is a free hero and the other hero is held (action FC .. FF) by this same captor (hero +
0x240 = the captor's word): the capture is made on the held hero. Not in Shan-Yu's room (the fiftieth glue).

'''
s = s.replace(a, hdr + a)
b = " [--ownabil]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--onevictim]")

i = s.index("def main():")
src = '''# ---- fifty-ninth glue (only with --onevictim) ---------------------------------------------------------------
GK_AT = 0x000EBF40
GK_END = 0x000EC000
GK_SRC = """
gk_cap:                           # jump at 0x00180378, in front of tg_cap. a0 = the captor's motion part, a1 = the victim, a2 = the move
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gk_go             # one hero: as before
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    bne t4,t6,gk_h
    nop
    lw t4,0x2400(t5)              # (the pointer stands on the twin for a moment: the main class's last hero)
gk_h:
    beq t4,zero,gk_go
    nop
    beq a1,t6,gk_other            # the victim is the twin: the other hero is player 1's
    move t3,t4
    bne a1,t4,gk_go               # the victim is no hero
    move t3,t6
gk_other:                         # t3 = the other hero
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    beq t2,t1,gk_go               # Shan-Yu's room: the fiftieth glue's pairs rule there
    lw t2,0x154(a1)               # the victim's action
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,gk_go               # the victim is held already (FC .. FF): the capture is his
    lw t2,0x154(t3)               # the other hero's action
    andi t2,t2,0xFFFC
    bne t2,t1,gk_go               # the other hero is not held: the capture is the victim's
    lw t2,0x240(t3)               # the captor's word the other hero was held with
    lw t0,0(a0)
    bne t2,t0,gk_go               # another captor holds him
    nop
    move a1,t3                    # THE SAME CAPTOR HOLDS THE OTHER HERO: the capture goes on with him
gk_go:
    j CAP_NEXT
    nop
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--onevictim" in sys.argv:                                          # fifty-ninth glue (a boss that holds one hero captures that hero)
        cap_next = words.get(0x00180378)
        assert cap_next is not None and (cap_next >> 26) == 2, "--onevictim needs --together (the jump at 0x00180378)"
        labels, n = add_code(GK_AT, GK_END, GK_SRC, {"CAP_NEXT": (cap_next & 0x3FFFFFF) << 2},
                             "a boss that holds one hero makes its further captures on that hero")
        hook_base(0x00180378, cap_next, (2 << 26) | ((labels["gk_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first, does this captor hold the other hero")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
