"""One-off: tools/merge/merge_v7.py, thirty-seventh glue, second version (after run mkA of the eighth round):
(1) the parking word is cleared before a rescue starts, and the rescue's end trusts it only while "the twin" is
    really a King Mickey (class table 0x00352360): a Continue or a room change in the middle of a rescue cannot
    leave a stale pointer behind;
(2) the second Mickey's constructor counted the rescue a second time (save + 0x3DB0 / + 0x3DB2, the numbers the
    game's roll uses): one is taken off again.
Run once:  python -I tools/merge/edit_merge_v7_mickey2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "mb_count" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)


rep('''    sd s2,24(sp)
    jal 0x001D00A8                # the game's call: Mickey for the engine's player
    nop
@TWO@''', '''    sd s2,24(sp)
    lui t7,0x000E
    jal 0x001D00A8                # the game's call: Mickey for the engine's player
    sw zero,0x7C00(t7)            # (no twin is parked yet)
@TWO@''')
rep('''    lw s1,0x7C00(t7)              # the parked twin (0 = there is no second Mickey)
    beq s1,zero,me_one
    lui t6,0x000F
    lw s2,0x05CC(t6)              # the second Mickey
    lui t5,0x0035''', '''    lw s1,0x7C00(t7)              # the parked twin (0 = there is no second Mickey)
    sw zero,0x7C00(t7)
    beq s1,zero,me_one
    lui t6,0x000F
    lw s2,0x05CC(t6)              # the second Mickey
    beq s2,zero,me_one
    lui t5,0x0035
    lw t4,0(s2)
    ori t3,t5,0x2360              # King Mickey's class table 0x00352360
    bne t4,t3,me_one              # "the twin" is no Mickey (a Continue or a new room came between): one Mickey
    nop''')
rep('''    sw s1,0x05CC(t6)              # the twin is the twin again
    lui t7,0x000E
    sw zero,0x7C00(t7)
    ld a0,40(sp)''', '''    sw s1,0x05CC(t6)              # the twin is the twin again
    ld a0,40(sp)''')
rep('''    sw s2,-5812(t5)               # the parking place = player 1's hero
    jal 0x001781A8                # the game's attach for player 1's Mickey
    move a0,s1
''', '''    sw s2,-5812(t5)               # the parking place = player 1's hero
    lui t7,0x0033                 # mb_count: the second Mickey counted the rescue once more (save + 0x3DB0 / + 0x3DB2)
    lhu t6,-1824(t7)              # 0x0032F8E0
    beq t6,zero,mb_c2
    addiu t6,t6,-1
    sh t6,-1824(t7)
mb_c2:
    lhu t6,-1822(t7)              # 0x0032F8E2
    beq t6,zero,mb_att
    addiu t6,t6,-1
    sh t6,-1822(t7)
mb_att:
    jal 0x001781A8                # the game's attach for player 1's Mickey
    move a0,s1
''')
rep("MK_END = 0x000E8800", "MK_END = 0x000E8880")
rep("RH_AT = 0x000E8800\nRH_END = 0x000E8860", "RH_AT = 0x000E8880\nRH_END = 0x000E88E0")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
