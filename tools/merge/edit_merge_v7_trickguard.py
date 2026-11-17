"""One-off: THE SIXTY-SEVENTH GLUE of tools/merge/merge_v7.py (--trickguard): LUXORD DOES NOT FLINCH WHILE A HERO STANDS
IN HIS TRICK (ninth round, job 3: Data Luxord's long hold of player 1's hero).
READ in the scripts B_EX150 / B_EX150_LV99 (local/analysis/h/ai): when a hero loses a card or command trick, the hero's
hooked piece captures him with move 254 (FE) and starts Luxord's act "rc_card_failure" / "rc_card2_failure". That
act waits 100 steps (the card trick), then turns the hero into the card or the die (L10433 / L15372), and only
THAT ends the hero's captured motion (its "motion start 0"). The script's damage routine (OBJ_DAMAGE) starts the
damage act whenever "this damage is a reaction" (the script call (2,8), 0x0018F4C0): that REPLACES the failure act,
and nothing ever lets the hero go. In the one-hero game nobody can hit Luxord in those steps (the only hero is
held). With two heroes the other hero's hit does (run lxN: Luxord's HP falls 12 steps after the FE and his motion
is the damage motion).
THE GLUE: the script call (2,8) (table word 0x0034EF70) answers "no reaction" when the running script's object is
Luxord (object 0x05F8) or Data Luxord (0x09C8) and a hero stands in a captured motion of his (the held bit, the
hero's captor word = the object's word + 0x140). The hit still takes HP; Luxord's act goes on.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_trickguard.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--trickguard" in s:
    raise SystemExit("already there")

DOC = '''SIXTY-SEVENTH GLUE (built only with the option --trickguard): LUXORD DOES NOT FLINCH WHILE A HERO STANDS IN HIS
TRICK. A hero who loses Luxord's card or command trick is captured (move 254) and Luxord's act "rc_card_failure" /
"rc_card2_failure" must run to its end: only it turns the hero into the card or the die and so ends his captured
motion. The script's damage routine starts the damage act on every hit that "is a reaction" (script call (2,8),
0x0018F4C0), which replaces that act: with two heroes the other hero's hit left the first one held (up to the
one-minute rule). lt_dmg (table word 0x0034EF70): for Luxord (object 0x05F8) and Data Luxord (0x09C8), while a
hero stands in a captured motion of his, the call answers "no reaction".

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- sixty-seventh glue (only with --trickguard) -------------------------------------------------------------
LT_AT = 0x000EE400
LT_END = 0x000EE4C0
LT_SRC = """
lt_dmg:                           # the script call (2,8) "is this damage a reaction": a0 = the call's slot (in: the damage, out: 0 / 1)
    lui t7,0x0035
    lw t0,-10076(t7)              # the running script (0x0034D8A4)
    beq t0,zero,lt_go
    nop
    lw t1,56(t0)                  # its object
    beq t1,zero,lt_go
    nop
    lw t2,8(t1)
    beq t2,zero,lt_go
    nop
    lw t2,0(t2)                   # its object number
    xori t3,t2,0x05F8             # Luxord
    beq t3,zero,lt_lux
    xori t3,t2,0x09C8             # Data Luxord
    bne t3,zero,lt_go
    nop
lt_lux:
    lw t4,0x140(t1)               # the word a hero in his hold carries
    beq t4,zero,lt_go
    nop
    lw t5,0x2400(t7)              # player 1's hero
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    addiu t8,zero,2
lt_hero:
    beq t5,zero,lt_next
    nop
    lw t2,0x160(t5)
    andi t2,t2,0x4000             # in a captured motion
    beq t2,zero,lt_next
    nop
    lw t2,0x240(t5)
    bne t2,t4,lt_next             # not this Luxord's
    nop
    jr ra                         # a hero stands in Luxord's trick: no reaction, Luxord's act goes on
    sw zero,0(a0)
lt_next:
    addiu t8,t8,-1
    bne t8,zero,lt_hero
    daddu t5,t6,zero
lt_go:
    j 0x0018F4C0                  # the game's routine
    nop
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--trickguard" in sys.argv:                                         # sixty-seventh glue (Luxord does not flinch while a hero stands in his trick)
        labels, n = add_code(LT_AT, LT_END, LT_SRC, {}, "Luxord takes no damage reaction while a hero stands in his trick")
        hook_game(0x0034EF70, 0x0018F4C0, labels["lt_dmg"], "the script call (2,8) 'is this damage a reaction': not for Luxord while he holds a hero")
        n_glue += n + 1

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
