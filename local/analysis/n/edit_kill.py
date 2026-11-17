"""One-off edit of tools/lane-n/make_down.py: Cure range for the other hero, --no-die, test-only --kill."""
import pathlib

p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
NL = chr(10)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:60])
    s = s.replace(old, new)


# ---- 1. range check in n_cure -------------------------------------------------------------------------------
rep("""n_cu_do:
    move a0,t0
""", """n_cu_do:
    lwc1 f0,0x70(t3)              # the game's script only heals friends close to the caster (measured: Goofy is
    lwc1 f1,0x70(s1)              # healed at 280 units and not at 289): the same limit for the other hero
    sub.s f0,f0,f1
    mul.s f0,f0,f0
    lwc1 f1,0x74(t3)
    lwc1 f2,0x74(s1)
    sub.s f1,f1,f2
    mul.s f1,f1,f1
    add.s f0,f0,f1
    lwc1 f1,0x78(t3)
    lwc1 f2,0x78(s1)
    sub.s f1,f1,f2
    mul.s f1,f1,f1
    add.s f0,f0,f1                # squared distance caster - other hero
    lui t7,RANGE2_HI
    ori t7,t7,RANGE2_LO
    mtc1 t7,f1
    c.le.s f0,f1
    bc1f n_cu_end                 # too far away
    nop
    lw t0,0(s0)
    move a0,t0
""")

# ---- 2. test-only forced falls ------------------------------------------------------------------------------
rep("""n_tick:                           # a0 = player object, every frame, before the game's own update
""", """n_tick:                           # a0 = player object, every frame, before the game's own update
@KILL@
""")

rep("""    dbg = ""
""", """    kill_src, kill_tab = "", ""
    if "--kill" in args:       # TEST ONLY: WHO@FRAME,... makes hero | twin | f0 | f1 (friends) lose all HP at that frame
        i = args.index("--kill")
        ents = []
        for item in args[i + 1].split(","):
            who, _, fr = item.partition("@")
            ents.append((int(fr) - 152, {"hero": 0, "twin": 1, "f0": 2, "f1": 3}[who]))
        del args[i:i + 2]
        kill_src = KILL_SRC
        NL = chr(10)
        kill_tab = NL + "n_k_table:" + NL + "".join("    .word %d" % c + NL + "    .word %d" % w + NL for c, w in ents) + "    .word 0" + NL
        SYM.update(CNT=0x0034D4BC, FRIENDS=0x01C60528)
    rng = 285.0
    if "--cure-range" in args:
        rng = float(args[args.index("--cure-range") + 1])
    bits = struct.unpack("<I", struct.pack("<f", rng * rng))[0]
    SYM["RANGE2_HI"], SYM["RANGE2_LO"] = bits >> 16, bits & 0xFFFF
    dbg = ""
""")

rep("""words, syms = assemble(CAVE, SRC.replace("@DEBUG@" + chr(10), dbg).replace("@DEBUG2@" + chr(10), dbg2), SYM)""",
    """words, syms = assemble(CAVE, (SRC + kill_tab).replace("@DEBUG@" + chr(10), dbg).replace("@DEBUG2@" + chr(10), dbg2)
                           .replace("@KILL@" + chr(10), kill_src), SYM)""")

rep('''def main():
    args = sys.argv[1:]
''', '''KILL_SRC = """    lui t7,%hi(G_PLAYER)          # TEST ONLY (--kill): once per step, when the game's counter reaches a table
    lw t6,%lo(G_PLAYER)(t7)       # entry, that unit loses all its HP through its own HP-change method
    bne a0,t6,n_k_skip
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd s0,16(sp)
    lui s0,%hi(n_k_table)
    addiu s0,s0,%lo(n_k_table)
n_k_loop:
    lw t0,0(s0)                   # counter value of this entry (0 = end of the table)
    beq t0,zero,n_k_done
    nop
    lui t7,%hi(CNT)
    lw t2,%lo(CNT)(t7)
    subu t2,t2,t0
    sltiu t2,t2,2                 # counter is at the entry's value or one behind it
    beq t2,zero,n_k_next
    nop
    lw t4,4(s0)                   # who: 0 hero, 1 twin, 2 / 3 the friends
    lui t7,%hi(G_PLAYER)
    lw a0,%lo(G_PLAYER)(t7)
    beq t4,zero,n_k_go
    nop
    lui t7,%hi(V_TWIN)
    lw a0,%lo(V_TWIN)(t7)
    addiu t5,t4,-1
    beq t5,zero,n_k_go
    nop
    sll t5,t4,2
    lui t7,%hi(FRIENDS)
    addiu t7,t7,%lo(FRIENDS)
    addu t7,t7,t5
    lw a0,-8(t7)
n_k_go:
    beq a0,zero,n_k_next
    nop
    lw t7,0x7F8(a0)
    andi t7,t7,4
    bne t7,zero,n_k_next          # already fallen
    nop
    lw t7,0(a0)
    lw t7,0x78(t7)
    addiu a1,zero,-9999
    move a2,zero
    jalr t7
    move a3,zero
n_k_next:
    b n_k_loop
    addiu s0,s0,8
n_k_done:
    ld ra,0(sp)
    ld a0,8(sp)
    ld s0,16(sp)
    addiu sp,sp,32
n_k_skip:
"""


def main():
    args = sys.argv[1:]
''')

rep('''(("--no-tick", "n_tick"), ("--no-hp", "n_hp"), ("--no-heal", "n_heal"), ("--no-cure", "n_cure")):''',
    '''(("--no-die", "n_die"), ("--no-tick", "n_tick"), ("--no-hp", "n_hp"), ("--no-heal", "n_heal"),
                        ("--no-cure", "n_cure")):''')

rep("""  python -I tools/lane-n/make_down.py <outDir> [--base DIR] [--time N] [--no-tick] [--no-hp] [--no-heal] [--extra FILE]
""", """  python -I tools/lane-n/make_down.py <outDir> [--base DIR] [--time N] [--cure-range N] [--extra FILE]
         [--no-die] [--no-tick] [--no-hp] [--no-heal] [--no-cure] [--debug] [--kill WHO@FRAME,...]

  --cure-range N  how close the other hero must be to the caster to share a hero's Cure (default 285, the
                  distance at which the game's own Cure stops reaching a friend)
  --no-...   leave one of the five hooks out (test variants)
  --debug    TEST ONLY: trace words at 0x000F2F80-0x000F2FBF and 0x000F2FE0-0x000F2FEF
  --kill     TEST ONLY: WHO = hero | twin | f0 | f1 loses all HP at that session frame (the same on both PCs)
""")
p.write_text(s, encoding="utf-8")
print("ok")
