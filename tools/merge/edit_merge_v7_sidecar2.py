"""One-off: tools/merge/merge_v7.py gets the FIFTY-FIFTH GLUE (built only with --sidecar2; an experiment for the
sidecar of the vehicle items): A SECOND HERO ON THE SIDECAR GETS THE SIDECAR'S OWN STATE.
It needs a second sidecar hero (object 0x0840) in the room: the seventh round's test disc test-s1-tt137sp3.iso has
one; the delivered disc has not.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_sidecar2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gz_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-FIFTH GLUE (built only with the option --sidecar2; an experiment): A SECOND HERO ON THE SIDECAR.
Read in the program: the sidecar's manager puts THE ENGINE'S PLAYER (the hero object 0x0840, Sora on the machine)
into the action state 53 (0x002E2074) and the object 0x0841 into state 54 (0x002E2098), and sets bit 0 of object
+ 0x108 on both. A second sidecar hero from the room data was left in the normal state (the seventh round's fault
lines at 0x00177008: a normal "Attack" on an object without an attack table).
gz_tick (the call at 0x00138538): when both heroes are sidecar heroes and player 1's hero is in state 53, player
  2's hero is put into state 53 too.

'''
s = s.replace(a, hdr + a)
b = " [--escape2]"
assert s.count(b) == 1
s = s.replace(b, b + " [--sidecar2]")

i = s.index("def main():")
src = '''# ---- fifty-fifth glue, an experiment (only with --sidecar2) ------------------------------------------------
GZ_AT = 0x000EBA00
GZ_END = 0x000EBB00
GZ_SRC = """
gz_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,zk_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,zk_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x0840
    bne t2,t1,zk_go               # he is no sidecar hero
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,zk_go
    lui t3,0x01C6
    ori t3,t3,0x0450              # the handler of state 53 (0x01C60450, the word at 0x0034E9F8 + 4 * 53)
    lw t2,0xC(t4)
    bne t2,t3,zk_go               # the ride has not begun for player 1's hero
    lw t2,0xC(t6)
    beq t2,t3,zk_go               # the twin is in state 53 already
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd t6,8(sp)
    move a0,t6
    jal 0x0016BD60                # the twin goes into state 53, as the manager does it for the hero
    addiu a1,zero,53
    ld t6,8(sp)
    lw t2,0x108(t6)
    ori t2,t2,0x1
    sw t2,0x108(t6)
    ld ra,0(sp)
    addiu sp,sp,16
zk_go:
    j TICK_NEXT
    move a0,zero
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--sidecar2" in sys.argv:                                           # fifty-fifth glue, an experiment (a second hero on the sidecar)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GZ_AT, GZ_END, GZ_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero on the sidecar gets the sidecar's state")
        hook_base(0x00138538, tick_next, jal(labels["gz_tick"]), "the field's START look-out: first, the second sidecar hero's state")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
