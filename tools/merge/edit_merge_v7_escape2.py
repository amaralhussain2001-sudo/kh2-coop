"""One-off: tools/merge/merge_v7.py gets the FIFTY-FOURTH GLUE (built only with --escape2; an experiment for the
carpet escape of the vehicle items): A SECOND HERO IN THE CARPET ESCAPE, WITH HIS OWN CARPET.
It needs a second escape hero (object 0x05E9) in the room: the seventh round's test disc test-s1-tt137sp3.iso has
one; the delivered disc has not.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_escape2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "ge_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-FOURTH GLUE (built only with the option --escape2; an experiment): A SECOND HERO IN THE CARPET ESCAPE.
Read in the program: the escape's manager puts THE ENGINE'S PLAYER into the action state 24 (0x002E0CCC) and the
escape's carpet (object 0x05EA, found by number) into state 25 (0x002E0CF0), and sets bit 0 of object + 0x108 on
both. State 24's routine 0x002E1998 works on the hero it is handed: it takes the manager's path matrix and keeps
that hero inside the moving path. State 25's routine 0x002E1D28 (the word at 0x00362E18) puts the carpet at the
engine's player (0x002E1D70). A second escape hero from the room data was left in the normal state with no
carpet (the seventh round's "confused pictures" and fault lines at 0x00177008).
ge_tick (the call at 0x00138538): when both heroes are escape heroes (object 0x05E9) and player 1's hero is in
  state 24, player 2's hero is put into state 24 too, and ONE second escape carpet is made at his place with the
  game's own routine and put into state 25 (0x000E7E60 the carpet, 0x000E7E64 its class word, 0x000E7E68 tries).
ge_upd (the word at 0x00362E18): the second carpet's state routine runs with player 2's hero as "the player".

'''
s = s.replace(a, hdr + a)
b = " [--norec]"
assert s.count(b) == 1
s = s.replace(b, b + " [--escape2]")

i = s.index("def main():")
src = '''# ---- fifty-fourth glue, an experiment (only with --escape2) ------------------------------------------------
GE_AT = 0x000EB840
GE_END = 0x000EBA00
GE_SRC = """
ge_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,ek_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,ek_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x05E9
    bne t2,t1,ek_go               # he is no escape hero
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,ek_go
    lui t3,0x01C6
    ori t3,t3,0x01B0              # the handler of state 24
    lw t2,0xC(t4)
    bne t2,t3,ek_go               # the escape has not begun for player 1's hero
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t6,8(sp)
    lw t2,0xC(t6)
    beq t2,t3,ek_carp             # the twin is in state 24 already
    nop
    move a0,t6
    jal 0x0016BD60                # the twin goes into state 24, as the manager does it for the hero
    addiu a1,zero,24
    ld t6,8(sp)
    lw t2,0x108(t6)
    ori t2,t2,0x1
    sw t2,0x108(t6)
    lui t7,0x000E
    sw zero,0x7E60(t7)            # a new escape: the second carpet of an older one is forgotten
    sw zero,0x7E68(t7)
ek_carp:
    lui t7,0x000E
    lw t9,0x7E60(t7)              # the second carpet
    beq t9,zero,ek_make
    nop
    lw t2,0(t9)
    lw t1,0x7E64(t7)
    bne t2,t1,ek_make             # it is gone
    lui t3,0x01C6
    ori t3,t3,0x01C0              # the handler of state 25
    lw t2,0xC(t9)
    beq t2,t3,ek_out              # alive and in state 25
    nop
    beq t2,zero,ek_out            # (no action part yet: the next step)
    move a0,t9
    sd t9,32(sp)
    jal 0x0016BD60                # the carpet's state 25, as the manager does it for the game's carpet
    addiu a1,zero,25
    ld t9,32(sp)
    lw t2,0x108(t9)
    ori t2,t2,0x1
    b ek_out
    sw t2,0x108(t9)
ek_make:
    lw t2,0x7E68(t7)
    sltiu t0,t2,3
    beq t0,zero,ek_out            # never more than three tries
    addiu t2,t2,1
    sw t2,0x7E68(t7)
    sw zero,0x7E60(t7)
    ld t6,8(sp)
    lw t2,0x70(t6)                # the twin's place
    sw t2,16(sp)
    lw t2,0x74(t6)
    sw t2,20(sp)
    lw t2,0x78(t6)
    sw t2,24(sp)
    lw t2,0x7C(t6)
    sw t2,28(sp)
    mtc1 zero,f12
    addiu a0,zero,0x05EA          # the escape's carpet
    jal 0x0016F000                # the game's own "make an object"
    addiu a1,sp,16
    beq v0,zero,ek_out
    lui t7,0x000E
    sw v0,0x7E60(t7)
    lw t2,0(v0)
    sw t2,0x7E64(t7)              # its class word: the sign that it is alive (state 25 comes at the next step)
ek_out:
    ld ra,0(sp)
    addiu sp,sp,48
ek_go:
    j TICK_NEXT
    move a0,zero
ge_upd:                           # the word at 0x00362E18 (was 0x002E1D28): state 25's routine. a1 = the carpet
    lui t7,0x000E
    lw t6,0x7E60(t7)
    bne a1,t6,eu_go               # the game's own carpet: as the game
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,eu_go
    lui t5,0x0035
    addiu sp,sp,-32
    sd ra,0(sp)
    lw t4,-5816(t5)
    sd t4,8(sp)                   # the engine's player
    jal 0x002E1D28
    sw t6,-5816(t5)               # for this one call "the player" is the twin
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
eu_go:
    j 0x002E1D28
    nop
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--escape2" in sys.argv:                                            # fifty-fourth glue, an experiment (a second hero in the carpet escape)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GE_AT, GE_END, GE_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero in the carpet escape, with his own carpet")
        hook_base(0x00138538, tick_next, jal(labels["ge_tick"]), "the field's START look-out: first, the second escape hero and his carpet")
        hook_game(0x00362E18, 0x002E1D28, labels["ge_upd"], "the escape carpet's state routine: the second carpet follows player 2's hero")
        n_glue += n + 1

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
