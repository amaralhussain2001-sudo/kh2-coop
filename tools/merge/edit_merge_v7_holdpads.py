"""One-off: THE SIXTY-EIGHTH GLUE of tools/merge/merge_v7.py (--holdpads, with --holdpair): WHILE A BOSS HOLDS BOTH HEROES,
BOTH CONTROLLERS COUNT (ninth round, job 3: who steers Riku in the last Xemnas's hold).
Seen in the runs xeG / xeH / xeI (candidate v112, eh20 74, both Xemnas objects' HP written to 150): Xemnas names player
2's hero, the sixty-fifth glue's mirror puts player 1's hero into the same hold; Riku then moves with PLAYER 2's
stick only (xeH), not with player 1's (xeG): the player whose hero the boss named plays Riku, the other one is held
and has nothing to press. Plan row 37's rule for a scene with one hero ("his controller also drives the one hero")
is taken for a hold too:
pm_pad (the head of the calls at 0x00167E90, the controller task's update of record 1): while the two heroes of a
hold's pair (0x000E7EA0 / A4) are both held (bit 0x4000 of object + 0x160), the two logical controller records
(0x0034D6C0 and + 0x60) are made one after the game's update: held / pressed / released / repeat of either (without
START, 0x2: each player's START stays his own), and a LEFT stick at rest takes the other controller's. Each
record gets its own "held" word back before the game's next update (record 0 by the twenty-sixth glue's gm_pre,
record 1 here), as the twenty-sixth glue does it for the Gummi Menu. The right sticks (the cameras) stay apart.
Values: 0x000E7F80 the records were made one at the last frame, 0x7F88 controller 2's own held word, 0x7F90 what
either held at the last frame.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdpads.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--holdpads" in s:
    raise SystemExit("already there")

DOC = '''SIXTY-EIGHTH GLUE (built only with the option --holdpads, with --holdpair): WHILE A BOSS HOLDS BOTH HEROES, BOTH
CONTROLLERS COUNT. In a hold's pair the boss's script reads one hero's controller (in the last Xemnas's hold the
player whose hero he named plays Riku; the other player was held with nothing to press). pm_pad (head of the
calls at 0x00167E90): while both heroes of the sixty-fifth glue's pair are held, the two logical controller
records are made one after the game's update (buttons of either, without START; a left stick at rest takes the
other's); each record gets its own held word back before the next update.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- sixty-eighth glue (only with --holdpads) ----------------------------------------------------------------
PM_AT = 0x000EE4C0
PM_END = 0x000EE6C0
PM_SRC = """
pm_pad:                           # the call at 0x00167E90 (the controller task's update of record 1; a0 = record 1)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t6,0x7F80(t7)              # were the two records one for a hold at the last frame?
    beq t6,zero,pm_go
    nop
    ld t5,0x7F88(t7)              # then record 1 gets controller 2's own "held" word back first
    sd t5,0(a0)
pm_go:
    jal PM_NEXT                   # the game's update of record 1 (behind the other glues of this call)
    nop
    lui t7,0x000E
    lw t0,0x7EA0(t7)              # the two heroes of a hold's pair (the sixty-fifth glue)
    lw t1,0x7EA4(t7)
    beq t0,zero,pm_off
    nop
    beq t1,zero,pm_off
    nop
    lw t2,0x160(t0)
    lw t3,0x160(t1)
    and t2,t2,t3
    andi t2,t2,0x4000
    beq t2,zero,pm_off            # not both held
    lui t5,0x000F
    lw t2,0x2638(t5)
    bne t2,zero,pm_off            # the twenty-sixth glue has made the records one itself at this frame
    lui t6,0x0035
    addiu t6,t6,-10560            # record 0 (0x0034D6C0); record 1 is 0x60 further
    addiu t9,zero,-3              # every button but START (0x2): each player's START stays his own
    ld t0,0(t6)                   # held, controller 1
    ld t1,0x60(t6)                # held, controller 2
    sd t0,0x2640(t5)              # (kept for gm_pre)
    sd t1,0x7F88(t7)              # (kept for pm_pad)
    or t2,t0,t1
    and t2,t2,t9                  # held by either
    lw t3,0x7F80(t7)
    bne t3,zero,pm_have
    ld t3,0x7F90(t7)              # (what either held at the last frame)
    ld t4,8(t6)                   # the first frame: pressed and released of both
    ld t8,0x68(t6)
    or t4,t4,t8
    and t4,t4,t9
    ld t8,0x10(t6)
    ld t3,0x70(t6)
    or t8,t8,t3
    b pm_store
    and t8,t8,t9
pm_have:
    nor t4,t3,zero
    and t4,t4,t2                  # pressed = held now and not before
    nor t8,t2,zero
    and t8,t8,t3                  # released = held before and not now
pm_store:
    sd t2,0x7F90(t7)
    sd t2,0x2648(t5)
    andi t0,t0,2
    or t0,t0,t2
    sd t0,0(t6)                   # held
    andi t1,t1,2
    or t1,t1,t2
    sd t1,0x60(t6)
    ld t0,8(t6)                   # pressed
    andi t0,t0,2
    or t0,t0,t4
    sd t0,8(t6)
    ld t0,0x68(t6)
    andi t0,t0,2
    or t0,t0,t4
    sd t0,0x68(t6)
    ld t0,0x10(t6)                # released
    andi t0,t0,2
    or t0,t0,t8
    sd t0,0x10(t6)
    ld t0,0x70(t6)
    andi t0,t0,2
    or t0,t0,t8
    sd t0,0x70(t6)
    ld t0,0x18(t6)                # repeat: of either
    ld t1,0x78(t6)
    or t4,t0,t1
    and t4,t4,t9
    andi t0,t0,2
    or t0,t0,t4
    sd t0,0x18(t6)
    andi t1,t1,2
    or t1,t1,t4
    sd t1,0x78(t6)
    addiu t3,zero,1
    sw t3,0x7F80(t7)
    sw t3,0x2638(t5)              # gm_pre gives record 0 its own held word back at the next frame
    lw t0,0x2C(t6)                # the left sticks' strengths
    lw t1,0x8C(t6)
    bne t0,zero,pm_l1
    nop
    ld t2,0x80(t6)                # controller 1's is at rest: it takes controller 2's
    ld t3,0x88(t6)
    sd t2,0x20(t6)
    b pm_ret
    sd t3,0x28(t6)
pm_l1:
    bne t1,zero,pm_ret
    nop
    ld t2,0x20(t6)                # controller 2's is at rest: it takes controller 1's
    ld t3,0x28(t6)
    sd t2,0x80(t6)
    b pm_ret
    sd t3,0x88(t6)
pm_off:
    sw zero,0x7F80(t7)
pm_ret:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--holdpads" in sys.argv:                                           # sixty-eighth glue (while a boss holds both heroes, both controllers count)
        assert "--holdpair" in sys.argv, "--holdpads needs --holdpair"
        pm_next = words[0x00167E90]                                        # the head of the glues at the update of record 1
        assert (pm_next >> 26) == 3
        labels, n = add_code(PM_AT, PM_END, PM_SRC, {"PM_NEXT": (pm_next & 0x3FFFFFF) << 2},
                             "while a boss holds both heroes, both controllers count")
        hook_base(0x00167E90, pm_next, jal(labels["pm_pad"]), "the controller task: first, the two records of a hold's pair are made one")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
