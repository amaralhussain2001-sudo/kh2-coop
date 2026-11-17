"""One-off: tools/merge/merge_v6.py, thirteenth glue, third part: the helper class's own methods (class table
0x00345C08) run with the twin's follow memory for a helper that goes with the twin; one flag (the pass word)
says "the twin's memory is in", so nothing swaps twice."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "hp_meth" in t:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (t.count(old), old[:70])
    t = t.replace(old, new)


rep("HELP_END = 0x000F5700", "HELP_END = 0x000F5800")
# the methods: stubs + common wrapper, at the end of the glue source
rep('''hb_end:
    jal hp_full
    nop
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
"""
''', '''hb_end:
    jal hp_full
    nop
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
hp_m08:                           # the helper class's methods (class table 0x00345C08, words +0x08, +0x0C, +0x14, +0x20)
    lui t9,0x0010
    b hp_meth
    ori t9,t9,0xC7F0
hp_m0C:
    lui t9,0x0017
    b hp_meth
    ori t9,t9,0xDC98
hp_m14:
    lui t9,0x0011
    b hp_meth
    ori t9,t9,0x1520
hp_m20:
    lui t9,0x0017
    ori t9,t9,0xDC38
hp_meth:                          # a0 = the helper, t9 = the game's method. Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0(t7)
    bne t3,zero,hm_plain          # the twin's memory is in already
    lw t3,0x14(t7)
    bne a0,t3,hm_2
    lw t2,0x08(t7)
    bne t2,zero,hm_go
    nop
    jr t9
    nop
hm_2:
    lw t3,0x18(t7)
    bne a0,t3,hm_plain
    lw t2,0x0C(t7)
    bne t2,zero,hm_go
    nop
hm_plain:
    jr t9
    nop
hm_go:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    move s0,a0
    move s1,t9
    li t3,1
    jal hp_swap
    sw t3,0(t7)
    jal hp_table
    li a0,1
    jalr s1
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    lui t7,0x000F
    sw zero,0x5800(t7)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
"""
''')
rep('''    (0x00112444, 0x24E72388, "lo:hp_taskC", "third follow task: low half (was 0x00112388)"),
)
''', '''    (0x00112444, 0x24E72388, "lo:hp_taskC", "third follow task: low half (was 0x00112388)"),
    (0x00345C10, 0x0010C7F0, "data:hp_m08", "helper class table +0x08"),
    (0x00345C14, 0x0017DC98, "data:hp_m0C", "helper class table +0x0C"),
    (0x00345C1C, 0x00111520, "data:hp_m14", "helper class table +0x14"),
    (0x00345C28, 0x0017DC38, "data:hp_m20", "helper class table +0x20"),
)
''')
rep('''            else:
                w = (3 << 26) | ((labels[how[4:]] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (helpers): " + what''', '''            elif how.startswith("data:"):
                w = labels[how[5:]]
            else:
                w = (3 << 26) | ((labels[how[4:]] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (helpers): " + what''')
# the hook reads data words too: the program file holds them (the class table is in the data part of the same segment)
# the thinking hook: not when the twin's memory is in already; and it sets the flag
rep('''nr_help:                          # a helper thinks (a0). Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0x14(t7)                # the true member table, place 1''', '''nr_help:                          # a helper thinks (a0). Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0(t7)
    bne t3,zero,nr_body           # the twin's memory is in already
    nop
    lw t3,0x14(t7)                # the true member table, place 1''')
rep('''    sd s0,8(sp)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    jal nr_body
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    ld ra,0(sp)''', '''    sd s0,8(sp)
    li t3,1
    sw t3,0(t7)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    jal nr_body
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    lui t7,0x000F
    sw zero,0x5800(t7)
    ld ra,0(sp)''')
rep('''those tasks, so the twelfth glue's hook does the same swap for a helper that goes with the twin (nr_help).
''', '''those tasks, so the twelfth glue's hook does the same swap for a helper that goes with the twin (nr_help),
and so do four methods of the helper class (class table 0x00345C08, words +0x08, +0x0C, +0x14, +0x20: hp_meth;
+0x08 runs the helper's follow object, whose states read the place beside the leader at 0x0010E464). The pass
word 0x000F5800 is 1 while the twin's memory is in, so nothing swaps twice.
''')
p.write_text(t, encoding="utf-8")
print("ok")
