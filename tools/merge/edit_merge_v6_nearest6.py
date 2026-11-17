"""One-off: tools/merge/merge_v6.py, twelfth glue, sixth version: the rule "the nearer hero (or the hero in a
scripted move) is the player" also holds while an object's script CALLBACK runs (reaction, animation and damage
callbacks; entry 0x0016CCE8, the script's object at +56), not only while the object thinks. Seen in test
g7-thorn: the boss offers "Break Raid" from an animation callback of its script, so the command went to player
1's menu although the twin was the hero in the move."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "near_trig" in t:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''NEAR_SRC = """
near_think:                       # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
''', '''NEAR_SRC = """
near_trig:                        # jump at 0x0016CCE8 (its second word is now a nop): a callback of a script runs.
    move t8,a0                    # a0 = the script; its object is at +56
    li t9,1
    lw a0,56(a0)
    srl t7,a0,22
    li t6,6
    bne t7,t6,nr_body             # not an object (0x0180xxxx-0x01BFxxxx): as it is
    nop
    lw t7,1156(a0)
    bne t7,t8,nr_body             # not this object's own script: as it is
    nop
    b nr_core
    nop
near_think:                       # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    move t9,zero                  # t9: 0 = thinking, 1 = a callback (t8 = the script then)
nr_core:
    lui t7,0x000F
''')
rep('''nr_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
''', '''nr_body:
    bne t9,zero,nr_body2
    nop
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
nr_body2:
    move a0,t8                    # the script again
    addiu sp,sp,-48               # the two instructions that sat at 0x0016CCE8
    j 0x0016CCF0
    sd s0,0(sp)
''')
# the helper path keeps the callback's fifth argument (t0) over the swaps
rep('''    sd s0,8(sp)
    li t3,1
    sw t3,0(t7)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    jal nr_body
    move a0,s0
''', '''    sd s0,8(sp)
    sd t0,16(sp)
    li t3,1
    sw t3,0(t7)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    ld t0,16(sp)
    jal nr_body
    move a0,s0
''')
rep('''        origin[a] = "glue hook (nearest): an object thinks"
        origin[a + 4] = "glue hook (nearest): its delay slot"
        n_glue += len(code) + 2
''', '''        origin[a] = "glue hook (nearest): an object thinks"
        origin[a + 4] = "glue hook (nearest): its delay slot"
        n_glue += len(code) + 2
        a = 0x0016CCE8                 # a callback of an object's script runs
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (0x27BDFFD0, 0xFFB00000), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["near_trig"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (nearest): a callback of an object's script runs"
        origin[a + 4] = "glue hook (nearest): its delay slot"
        n_glue += 2
''')
rep('''his own script offers the follow-up commands.''', '''his own script offers the follow-up commands. The same rules hold
while a CALLBACK of an object's script runs (reaction, animation and damage callbacks: jump at 0x0016CCE8 to
near_trig; the script's object is at script +56 and must be an object whose own script this is): a boss offers
the follow-up command of a move from an animation callback (test g7-thorn).''')
p.write_text(t, encoding="utf-8")
print("ok")
