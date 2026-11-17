"""One-off: the SIXTY-THIRD GLUE of tools/merge/merge_v7.py (--ownkey), second form (ninth round, part 91).
Seen in runs kbA / kbB (candidate v98): ONE fault line "pc 0x00168B38, address 4" at each Keyblade change. The
recorder at 0x00168B38 (run kf2) names the caller: 0x00169FC4, the object's script start, with the object's model
file pointer (object + 0x7AC) = 0. Read: a weapon object binds to its model and effect files BY NAME AND NUMBER
(0x001A9218 -> 0x001708F8(name, number); the number comes from 0x00176168: 2301 for a hero's first hand), and
player 2's own Keyblade's files have the number 2303. The model is drawn all the same (it is found by name), but
the pointer stayed empty.
kb_ctor (the call at 0x00176204, was jal 0x00185468, the weapon object's constructor): for the twin's first hand,
when the weapon's model file is in the pool with the number 2303, the weapon gets the number 2303.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "kb_ctor" in s:
    raise SystemExit("already there")

a = '''kc_load:                          # call at 0x0017607C'''
assert s.count(a) == 1
b = '''kb_ctor:                          # call at 0x00176204 (was jal 0x00185468: the weapon object's constructor). a1 = the weapon's entry, a2 = the hero, t0 = the hand, t1 = the files' number
    bne t0,zero,kx_go             # the second hand
    addiu t6,zero,2301
    bne t1,t6,kx_go
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq a2,t6,kx_twin             # the twin (a change in the menu)
    lui t7,0x000E
    lw t6,0x7E88(t7)              # or the twin while he is built
    beq t6,zero,kx_go
    lui t6,0x000F
    lw t6,0x05C4(t6)
    bne t6,zero,kx_go
    nop
kx_twin:
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    sd t0,40(sp)
    sd t1,48(sp)
    move a0,a1
    jal 0x0016F470                # the name of the weapon's model file
    move a1,zero
    move a0,v0
    jal 0x00170240                # is it in the pool with the number 2303 (player 2's own Keyblade)
    addiu a1,zero,2303
    ld t1,48(sp)
    beq v0,zero,kx_r
    nop
    addiu t1,zero,2303            # yes: the weapon binds to those files
kx_r:
    ld t0,40(sp)
    ld a3,32(sp)
    ld a2,24(sp)
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,64
kx_go:
    j 0x00185468
    nop

'''
s = s.replace(a, b + a)
a = '''        hook_game(0x0017607C, jal(0x00170888), jal(labels["kc_load"]), "the weapon change's load: player 2's files are asked for again or let go")
        n_glue += n + 4
'''
assert s.count(a) == 1
b = '''        hook_game(0x0017607C, jal(0x00170888), jal(labels["kc_load"]), "the weapon change's load: player 2's files are asked for again or let go")
        hook_game(0x00176204, jal(0x00185468), jal(labels["kb_ctor"]), "a weapon object is made: the twin's own Keyblade binds to its files (number 2303)")
        n_glue += n + 5
'''
s = s.replace(a, b)
a = "weapon and files only." + NL
assert s.count(a) == 1
s = s.replace(a, "weapon and files only; kb_ctor (0x00176204): the twin's own Keyblade's weapon object gets the number 2303 of its" + NL + "files." + NL)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
