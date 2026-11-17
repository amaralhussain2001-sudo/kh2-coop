"""One-off: tools/merge/merge_v7.py gets the THIRTY-NINTH GLUE (an object that holds a hero in a paired move also
THINKS with that hero as the player). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_thinkheld.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "nt_held" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''THIRTY-NINTH GLUE (option --no-thinkheld leaves it out): AN OBJECT THAT HOLDS A HERO IN A PAIRED MOVE ALSO THINKS
WITH THAT HERO AS THE PLAYER (plan row 9, first step, third half).
What was there (run cap2, candidate v39, the recorder at 0x00180378): one clash of Shan-Yu MIXED the heroes: the
start (moves 0xFC, 0xFD) took the twin, the next pushes (0xFF, 0xFD) took player 1's hero, the end (0xFE) the twin
again. The thirty-sixth glue keeps "the hero who is held" for the script's CALLBACKS, but while the boss THINKS the
twelfth glue still hands in the NEARER hero, and part of the clash is started from there.
Now the jump at 0x0016A950 goes to nt_held first: for an object that is neither a hero nor a helper, the twin is
the player of its thinking while the twin is held by it (twin + 0x240 = the object, bit 0x4000 of + 0x160); while
player 1's hero is held by it the thinking runs as the game's (no "nearer" rule); otherwise the twelfth glue's
near_think (0x000F5000) decides as before.

'''
s = s.replace(a, hdr + a)
b = "[--no-reactheld]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-thinkheld]")
i = s.index("def main():")
src = '''# ---- thirty-ninth glue -------------------------------------------------------------------------------------
NT_AT = 0x000E88E0
NT_END = 0x000E8980
NT_SRC = """
nt_held:                          # jump at 0x0016A950 (was the twelfth glue's j near_think). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,nt_old
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nt_old
    nop
    beq a0,t4,nt_old              # the heroes and the helpers: the old rule
    nop
    beq a0,t6,nt_old
    lw t3,0(a0)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nt_old
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,a0,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nt_body                   # it thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,a0,nt_old
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    beq t3,zero,nt_old
    nop
nt_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
nt_old:
    j 0x000F5000                  # the twelfth glue's near_think
    nop
"""
NT_BASE_WORD = (0x0016A950, 0x0803D400)            # the base patch: j near_think (0x000F5000)


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-thinkheld" not in sys.argv:                                   # thirty-ninth glue
        labels, n = add_code(NT_AT, NT_END, NT_SRC, {}, "an object that holds a hero in a paired move thinks with that hero as the player")
        a, w0 = NT_BASE_WORD
        hook_base(a, w0, (2 << 26) | ((labels["nt_held"] >> 2) & 0x3FFFFFF), "an object thinks: first the hero it holds, then the twelfth glue's rule")
        n_glue += n

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
