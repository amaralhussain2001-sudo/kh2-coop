"""One-off: tools/merge/merge_v7.py gets the FORTY-FIRST GLUE (the files of a second Drive Form are loaded BEHIND
the files in use, and a second form is refused only when the object file pool has no room for it).
The record of the edit; run once:  python -I tools/merge/edit_merge_v7_formbase.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "fb_req" in s:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70])
    s = s.replace(old, new)


a = "  python -I tools/merge/merge_v7.py [outDir]"
hdr = '''FORTY-FIRST GLUE (option --no-formbase leaves it out; needs the thirty-fourth): THE FILES OF A SECOND DRIVE FORM
GO BEHIND THE FILES IN USE, AND A SECOND FORM IS REFUSED ONLY WHEN THE FILE POOL HAS NO ROOM (plan row 44, fault F6).
What was there (runs tfpm / fp1 of the eighth round, probe tools/own/filepool_probe.py): the loader keeps every
object file in one pool (list head 0x0034DCA0, limit word 0x0034DCB0 = the start of the object heap), laid out in
the order of the files' keep-numbers. A form's files are asked for with the numbers 5000 (the body), 5001 and 5002
(its weapons). With player 1 in Valor, player 2's Wisdom body (three files, 2.1 MB, number 5000) is put in FRONT of
Valor's weapon files (5001 / 5002): they move from 21,893,184 to 24,021,056 and are loaded again there, while
player 1's Keyblade still points at the old data. His body's next update calls into the destroyed data: the C++
runtime's "pure virtual method called", abort(), and the game leaves to the PS2 browser. The memory itself was
enough: 1.38 MB of the pool stayed free with both forms.
Now:
(1) fb_req (the form task's file request at 0x001B6700): while the OTHER hero is in a form, the changing hero's
    files are asked for with a number base 10 above the other hero's base (5010, 5020 ...), so they are laid out
    behind everything in use and nothing moves. Each hero's base is kept at 0x000E7C04 / 0x000E7C08. With no twin,
    or when the other hero is in no form: 5000, as the game.
(2) the thirty-fourth glue's judge of a form row (fm_ask_judge) now also asks, for a SECOND form only: is there
    room? Room = the pool's limit minus the end of the last file that may not be thrown out (keep-number below
    10000); it must be at least the form's need (table fa_need, measured in runs fp1 to fp5 + 64 KB). No room =
    the row is dim, exactly like a form whose helper is away.

'''
assert s.count(a) == 1
s = s.replace(a, hdr + a)
rep("[--no-helperform]", "[--no-helperform] [--no-formbase]")

# (2) the judge
rep('''fm_ask_list:                      # from 0x001BEB68 (was jal 0x001C8DB8): s0 = the control object whose list is built
    b fm_ask
    lw t9,0x9E0(s0)               # its hero
fm_ask_judge:                     # from 0x001BC594 (was jal 0x001C8DB8): s0 = the hero whose row is judged
    move t9,s0
fm_ask:''', '''fm_ask_list:                      # from 0x001BEB68 (was jal 0x001C8DB8): s0 = the control object whose list is built
    move t8,zero                  # (no row: no question about room)
    b fm_ask
    lw t9,0x9E0(s0)               # its hero
fm_ask_judge:                     # from 0x001BC594 (was jal 0x001C8DB8): s0 = the hero whose row is judged,
    move t8,s1                    # s1 = the row's command
    move t9,s0
fm_ask:''')
rep('''    bne t6,zero,fa_no             # the twin is in a form (the asker is not): bit 0 means forms -> free for him
    nop''', '''    bne t6,zero,fa_mem            # the twin is in a form (the asker is not): bit 0 means forms -> free for him,
    nop                           # if there is room for a second form's files''')
rep('''    bne t6,zero,fa_no             # player 1's hero is in a form (the asker is not)
    nop
fa_yes:''', '''    bne t6,zero,fa_mem            # player 1's hero is in a form (the asker is not)
    nop
fa_yes:''')
rep('''fa_bit0:
    jr ra
    sltu v0,zero,t7
''', '''fa_bit0:
    jr ra
    sltu v0,zero,t7
fa_mem:                           # @FORMBASE@ a SECOND form: only when the object file pool has room for its files
    beq t8,zero,fa_no             # the list as a whole: yes
    nop
    lhu t6,2(t8)
    addiu t6,t6,-4
    bne t6,zero,fa_no             # not a form row
    nop
    lh t6,4(t8)                   # the form number
    sltiu t5,t6,7
    beq t5,zero,fa_no
    sll t6,t6,2
    lui t5,%hi(fa_need)
    addiu t5,t5,%lo(fa_need)
    addu t5,t5,t6
    lw t3,0(t5)                   # what this form needs
    lui t5,0x0035
    lw t4,-9056(t5)               # the file list (0x0034DCA0)
    lw t2,-9040(t5)               # the pool's limit (0x0034DCB0)
    move t1,zero                  # the end of the last file that must stay
fa_walk:
    beq t4,zero,fa_sum
    nop
    lw t6,40(t4)                  # its keep-number
    slti t5,t6,10000
    beq t5,zero,fa_next           # it may be thrown out: not counted
    lw t6,48(t4)                  # its place
    lw t5,44(t4)                  # its size
    addu t6,t6,t5
    sltu t5,t1,t6
    movn t1,t6,t5
fa_next:
    b fa_walk
    lw t4,60(t4)
fa_sum:
    subu t2,t2,t1                 # room
    sltu t5,t2,t3
    jr ra
    move v0,t5                    # 1 = no room: the row is dim
fa_need:                          # bytes of the pool a form's files need (measured + 0x10000), forms 0 to 6
    .word 0x7FFFFFFF
    .word @NEED1@
    .word @NEED2@
    .word @NEED3@
    .word @NEED4@
    .word @NEED5@
    .word 0x7FFFFFFF
''')
rep("FM_AT = 0x000E8300\nFM_END = 0x000E8440", '''FM_AT = 0x000E8300
FM_END = 0x000E8600
FORM_NEED = {1: 2217984, 2: 2336768, 3: 3145728, 4: 3145728, 5: 3145728}   # Valor, Wisdom measured (fp1); 3 to 5: see fp3-fp5''')

# (1) the request
i = s.index("def main():")
src = '''# ---- forty-first glue --------------------------------------------------------------------------------------
FB_AT = 0x000E8CC0
FB_END = 0x000E8D80
FB_SRC = """
fb_req:                           # from 0x001B6700 (was jal 0x0016EF28; a0 = the form, from the delay slot). s2 = the
    lui t5,0x000F                 # form record: its first word is the body that changes
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fb_plain          # one hero: as the game
    nop
    lw t6,0(s2)
    lui t3,0x000E
    bne t6,t4,fb_p1
    nop
    lui t7,0x0033                 # the twin changes: the other hero is player 1's
    lbu t6,-4012(t7)              # his form (the save's byte 0x0032F054)
    lw t2,0x7C04(t3)              # the number base of his form's files
    b fb_have
    addiu t1,t3,0x7C08            # where the twin's base is kept
fb_p1:
    lbu t6,0x47E8(t5)             # player 1's hero changes: the twin's form
    lw t2,0x7C08(t3)
    addiu t1,t3,0x7C04
fb_have:
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fb_go             # the other hero is in no form: 5000, as the game
    addiu t0,zero,5000
    bne t2,zero,fb_add
    nop
    addiu t2,zero,5000            # (his form was built with a room: the game's numbers)
fb_add:
    addiu t0,t2,10                # behind his files
fb_go:
    sw t0,0(t1)
    addiu sp,sp,-16
    sd ra,0(sp)
    sd t0,8(sp)
    jal 0x001D1438                # the form's object id
    nop
    move a0,v0
    ld a1,8(sp)
    ld ra,0(sp)
    addiu a2,zero,4
    addiu a3,zero,7
    j 0x0016EB48                  # the game's request, with this number base
    addiu sp,sp,16
fb_plain:
    j 0x0016EF28
    nop
"""
FB_HOOK = (0x001B6700, 0x0C05BBCA)                 # jal 0x0016EF28


'''
s = s[:i] + src + s[i:]
# the build steps: the judge's part is inside FM_SRC (switched by the option), the request is new
rep('''        labels, n = add_code(FM_AT, FM_END, FM_SRC, {}, "two Drive Forms at once: the form lock is judged for each hero")''',
    '''        fm_src = FM_SRC
        for k in range(1, 6):
            fm_src = fm_src.replace("@NEED%d@" % k, "0x%08X" % (0 if "--no-formbase" in sys.argv else FORM_NEED[k] + 0x10000))
        labels, n = add_code(FM_AT, FM_END, fm_src, {}, "two Drive Forms at once: the form lock is judged for each hero")''')
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-formbase" not in sys.argv and "--no-twoforms" not in sys.argv:     # forty-first glue
        labels, n = add_code(FB_AT, FB_END, FB_SRC, {}, "the files of a second Drive Form are asked for with a number base behind the files in use")
        a, w0 = FB_HOOK
        hook_game(a, w0, jal(labels["fb_req"]), "the form task asks for the form's files: behind the other hero's form files")
        n_glue += n + 1

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
