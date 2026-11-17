"""One-off: replace the sixth glue of tools/merge/merge_v6.py (first try: hook 0x00189E3C) by the wrapper of the
whole routine 0x00189E18 (Reaction Commands are offered to both heroes)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "react_both" in t:
    raise SystemExit("already there")
a = t.index("SIXTH GLUE: THE SECOND HERO'S ACTION REGISTERS WITH HIS OWN CONTROL OBJECT.")
b = t.index("  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-react]")
t = t[:a] + '''SIXTH GLUE: REACTION COMMANDS ARE OFFERED TO BOTH HEROES.
What was there (lane S1 rows TTR-10 and TTR-15; VERIFIED again, tests h1-dusk-p1 / h1-dusk-p2): in the Old
Mansion fight where the Dusk cannot be damaged the story goes on after player 1's attacks (scene by frame 8900)
and never after player 2's; in every fight the prompts went "to S only". The bit-coded search (tests
h2-plbit0..6: the scene came in variants 0, 3 and 4 = index 25) found routine 0x00189E18(source object, command,
argument), reached from 0x00189490: it builds a target record and offers the command to the control object of
THE ENGINE'S PLAYER (object+0xB44): through 0x001BD418 when the source is that player himself, through
0x001BD3E0 when the source is anything else (an enemy, an object); on success it notes the command in the
player object (+0x50C, flag 0x20000 at +0x160).
Now (hook at the routine's entry 0x00189E18, routine react_both at 0x000F4A00): the source is the twin -> the
routine runs once with the twin as "the player" (his own control object, lane G's S2); the source is player 1's
hero -> as before; the source is anything else -> the routine runs twice, for player 1's hero and for the twin.
"The twin as the player" = the pointer 0x0034E948 holds the twin for the length of that one call.
(A first try, only "the twin's own action counts as the player's", did not let the story go on: test
h3-dusk-react.)

''' + t[b:]
a = t.index("REACT_AT = 0x000F48E0")
b = t.index("\nHOOKS = (", a)
t = t[:a] + '''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00
REACT_SRC = """
react_both:                       # hook 0x00189E18 (j; the routine's second instruction runs in the delay slot).
    lui t6,0x000F                 # a0 = source object, a1 = command, a2 = argument
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,rb_plain          # no twin: the routine as it is
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq a0,t4,rb_plain            # player 1's hero is the source: as it is
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s0,a0
    move s1,a1
    move s2,a2
    beq a0,t6,rb_twin             # the twin is the source: only for him
    move s3,t6
    jal rb_orig                   # an enemy or an object is the source: first for player 1's hero
    nop
rb_twin:
    lui t5,0x0035
    lw t4,-5816(t5)
    sd t4,40(sp)                  # the engine's player, to put back
    sw s3,-5816(t5)               # for this one call "the player" is the twin
    move a0,s0
    move a1,s1
    jal rb_orig
    move a2,s2
    ld t4,40(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,48
rb_plain:
rb_orig:                          # the routine itself
    addiu sp,sp,-80               # the instruction that sat at 0x00189E18
    j 0x00189E20
    lui t7,0x35                   # (0x00189E1C again)
"""
REACT_HOOK = (0x00189E18, 0x27BDFFB0, "a Reaction Command is offered: to the hero it belongs to, or to both heroes")
''' + t[b:]
old = '''        a, orig, what = REACT_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DF0E948), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["react_own"] >> 2) & 0x3FFFFFF)'''
new = '''        a, orig, what = REACT_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x3C0F0035), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["react_both"] >> 2) & 0x3FFFFFF)'''
assert t.count(old) == 1
t = t.replace(old, new)
old = '''            origin[a] = "glue (the second hero's action registers with his own control object)"'''
assert t.count(old) == 1
t = t.replace(old, '''            origin[a] = "glue (Reaction Commands are offered to both heroes)"''')
p.write_text(t, encoding="utf-8")
print("ok")
