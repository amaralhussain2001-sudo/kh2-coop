"""One-off: tenth glue of tools/merge/merge_v6.py, second version: the hook is the entry of "an object thinks"
(0x0016A950: its script's main and its action list); the class table's update method made no difference."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "helper_think" in t:
    raise SystemExit("already there")
a = t.index("Now: the helpers' class (class table 0x00345C08) gets its update method")
b = t.index("  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-helper] [--react]")
t = t[:a] + """Now (jump at the entry of 0x0016A950 "an object thinks": it runs the object's script and its action list;
routine helper_think at 0x000F4E80): for the object in party place 2 (0x00348640), while a twin is there, the
engine's player pointer holds the twin for the length of that call. So everything that helper's script asks
about "the player" (where to go, whom to help) means the second hero. The helper in party place 1 and every
other object: unchanged.
(A first try through the helpers' class table, update method +0x0C = 0x0017DC98, changed nothing: test
l3-mu68-helper.)

""" + t[b:]
a = t.index('HELPER_SRC = """')
b = t.index("REACT_AT = 0x000F4A00")
t = t[:a] + '''HELPER_SRC = """
helper_think:                     # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,ht_body
    lui t5,0x0035
    lw t4,-31168(t5)              # 0x00348640: the party table's place 2 (the second helper)
    bne a0,t4,ht_body
    nop
    lw t4,-5816(t5)               # the engine's player
    beq t4,zero,ht_body
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal ht_body                   # he thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
ht_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
"""
HELPER_HOOK = (0x0016A950, 0x27BDFFF0, 0xFFB00000, "an object thinks: the second helper with the second hero as the player")

''' + t[b:]
old_a = t.index("        a, orig, what = HELPER_WORD")
old_b = t.index("        n_glue += len(code) + 1", old_a)
t = t[:old_a] + '''        a, w0, w1, what = HELPER_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["helper_think"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (helpers): " + what
        origin[a + 4] = "glue hook (helpers): its delay slot"
        n_glue += 1
''' + t[old_b:]
p.write_text(t, encoding="utf-8")
print("ok")
