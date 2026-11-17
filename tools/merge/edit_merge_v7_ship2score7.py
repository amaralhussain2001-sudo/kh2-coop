"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), sixth form (ninth round, STATE parts 103 to 106:
Gummi route 8 is flown differently since this glue).
FOUND (runs of tools/own/r9_chain50.sh): the counting half alone gives build 19's flight; the score rows alone give
the changed one; a loop that costs time in every frame does not change the flight. READ: a new picture
(0x01F46E80 -> 0x01F47148) is 388 bytes from the flight module's OWN HEAP (0x01F19160). Player 2's score row (a
frame, seven digits, an eighth) and the gauge's digit are ten such pictures: they lie in the heap in front of
every later enemy and shot, and the flight is not the same when its objects lie elsewhere.
NOW: the ten pictures of this glue lie in the PATCH'S OWN MEMORY (nine at 0x000EA210, 388 bytes each, the tenth at
0x000EB5E8; both stretches are gaps of the routine cave). gq_new stands in the picture maker's call of the
module's "new" (0x01F47164): while row 2 is in work or the gauge's digit is made, it hands out the next own
place (0x000E7F98 counts them); else, or when none is left, the module's heap as before. Such a picture must not
be ended with the module's "delete": gq_end ends a picture with the class's first method (destroy only,
0x01F47540) when it lies in the own memory, with the second (destroy and delete, 0x01F47598) when not. The
score rows' free routine ends row 2's nine pictures and the digit with gq_end.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score7.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gq_new:" in s:
    raise SystemExit("already there")

# 1. the picture maker's call of "new"
old = '''GQ_CALLS = (                                       # (a call in the flight module, its word, the routine that is called in its place)
    (0x01F679A8, 0x0C7D37B4, "gq_get"),            # the score row reads the score
)
'''
assert s.count(old) == 1
s = s.replace(old, '''GQ_CALLS = (                                       # (a call in the flight module, its word, the routine that is called in its place)
    (0x01F679A8, 0x0C7D37B4, "gq_get"),            # the score row reads the score
    (0x01F47164, 0x0C7C6458, "gq_new"),            # a new picture asks the module's heap for its 388 bytes
)
GQ_OWN_AT = 0x000EA210                             # nine own pictures (388 bytes each) for row 2 and the gauge's digit
GQ_OWN_LAST = 0x000EB5E8                           # the tenth
GQ_OWN_END = 0x000EB770                            # (an own picture lies in GQ_OWN_AT .. GQ_OWN_END)
''')

# 2. the free routine: row 2's pictures and the digit are ended with gq_end
a = s.index("gq_sdfree:                        # 0x01F676A8(a0 = the score row): its pictures are freed\n")
b = s.index("gqd_body:\n", a)
s = s[:a] + '''gq_sdfree:                        # 0x01F676A8(a0 = the score row): its pictures are freed
    lui t7,0x000E
    ori t6,t7,0x7F40
    beq a0,t6,gqd_body            # (a call for row 2 itself: not made any more)
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    jal gqd_body                  # the game's row
    nop
    lui s0,0x000E
    ori s0,s0,0x7F44              # row 2's pictures: its frame, seven digits, the eighth (row 2 + 4 .. + 36)
    addiu s1,zero,9
gqd_l:
    lw a0,0(s0)
    beq a0,zero,gqd_n
    nop
    jal gq_end
    nop
    sw zero,0(s0)
gqd_n:
    addiu s1,s1,-1
    bne s1,zero,gqd_l
    addiu s0,s0,4
    lui t7,0x000E
    lw a0,0x7F78(t7)              # the gauge's digit
    sw zero,0x7F68(t7)
    sw zero,0x7F78(t7)
    beq a0,zero,gqd_1
    sw zero,0x7F98(t7)            # no own place is given out any more
    jal gq_end
    nop
gqd_1:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32

gq_end:                           # a0 = a picture: it is ended; one in the own memory without the module's "delete"
    lw t6,0(a0)                   # its class
    lui t5,0x000E
    ori t5,t5,@OWN_LO@
    sltu t4,a0,t5
    bne t4,zero,gqe_heap
    lui t5,0x000E
    ori t5,t5,@OWN_HI@
    sltu t4,a0,t5
    beq t4,zero,gqe_heap
    nop
    lw t6,0(t6)                   # the first method: destroy only
    jr t6
    nop
gqe_heap:
    lw t6,4(t6)                   # the second: destroy and delete, as the game ends its own
    jr t6
    nop

gq_new:                           # the call at 0x01F47164 (was the module's "new", a0 = 388): a new picture's memory
    lui t7,0x000E
    lw t6,0x7F7C(t7)              # row 2 is in work, or the gauge's digit is being made
    beq t6,zero,gqw_heap
    lw t5,0x7F98(t7)              # how many own places are given out
    sltiu t4,t5,10
    beq t4,zero,gqw_heap          # none left: the module's heap
    addiu t4,t5,1
    sw t4,0x7F98(t7)
    addiu t4,zero,9
    beq t5,t4,gqw_last
    sll t3,t5,8
    sll t2,t5,7
    addu t3,t3,t2
    sll t2,t5,2
    addu t3,t3,t2                 # 388 x its number
    lui v0,0x000E
    ori v0,v0,@OWN_LO@
    jr ra
    addu v0,v0,t3
gqw_last:
    lui v0,0x000E
    jr ra
    ori v0,v0,@OWN_LAST@
gqw_heap:
    j 0x01F19160
    nop

''' + s[b:]

# 3. the gauge's digit is made in the own memory too
old = '''    jal 0x01F48038                # the HUD's picture sheet
    nop
    move a0,v0
    addiu a1,zero,8
    jal 0x01F46E80                # a new picture: a digit
    addiu a2,zero,72
    lui t7,0x000E
    beq v0,zero,gqs_out
    sw v0,0x7F78(t7)
'''
assert s.count(old) == 1
s = s.replace(old, '''    jal 0x01F48038                # the HUD's picture sheet
    nop
    lui t7,0x000E
    addiu t4,zero,1
    sw t4,0x7F7C(t7)              # (its memory: an own place)
    move a0,v0
    addiu a1,zero,8
    jal 0x01F46E80                # a new picture: a digit
    addiu a2,zero,72
    lui t7,0x000E
    sw zero,0x7F7C(t7)
    beq v0,zero,gqs_out
    sw v0,0x7F78(t7)
''')

# 4. the numbers of the own memory, and a check that no routine lies there
old = '''    src = GQ_SRC.replace("@ROW_DX@", str(GQ_ROW_DX))'''
assert s.count(old) == 1
s = s.replace(old, '''    src = GQ_SRC.replace("@OWN_LO@", "0x%04X" % (GQ_OWN_AT & 0xFFFF)).replace("@OWN_HI@", "0x%04X" % (GQ_OWN_END & 0xFFFF)).replace("@OWN_LAST@", "0x%04X" % (GQ_OWN_LAST & 0xFFFF))
    src = src.replace("@ROW_DX@", str(GQ_ROW_DX))''')
old = '''        hook_base(0x00167E90, gq_next, jal(labels["gq_inst"]), "the controller task: first the sixty-sixth glue's jumps into a fresh flight module")
        n_glue += n
'''
assert s.count(old) == 1
s = s.replace(old, old + '''        gq_own = list(range(GQ_OWN_AT, GQ_OWN_AT + 9 * 388, 4)) + list(range(GQ_OWN_LAST, GQ_OWN_LAST + 388, 4))
        assert GQ_OWN_LAST + 388 <= GQ_OWN_END and (GQ_OWN_AT >> 16) == (GQ_OWN_END >> 16) == 0x000E
        gq_own_check = True                                                # (checked at the end: no routine may lie in the own pictures' memory)
''')
old = '''    out.mkdir(parents=True, exist_ok=True)
    head = ['''
assert s.count(old) == 1
s = s.replace(old, '''    if "--ship2score" in sys.argv:
        clash = [a for a in gq_own if a in words]
        assert not clash, "the sixty-sixth glue's own pictures lie on patch words: %08X .." % clash[0]

''' + old)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
