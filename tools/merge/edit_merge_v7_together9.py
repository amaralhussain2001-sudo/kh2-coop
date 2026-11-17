"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue), NINTH form: THE SECOND HERO'S
COPY OF THE HOOKED SCRIPT MUST NOT STEP THE BOSS'S OWN BOOKKEEPING.
What was there (candidate v70, runs tg22 / tg23 against the controls tgc1 / tgc2 on build 15): with two heroes in
the clash the gate fell sooner. Read in Shan-Yu's script: the hero-side loop of the clash keeps the BOSS's numbers
(the push speed at work + 152, the clash's time limit at work + 156, the push count at work + 148): it lets the
speed grow 5 % a step and takes the step's time off the limit. Two copies of that loop did both twice a step: the
time limit ran out twice as fast and a press counted twice.
Read in the program: a script context (0x0016C8F8) keeps the program at + 0 and the WORK MEMORY at + 52; a hooked
context is made from the boss's own script (0x0016CF00), so it shares the boss's work memory. The work size is the
word at program + 16.
Now th_tick (the call at 0x00177510): when the hooked script that runs belongs to the SECOND hero of a living
pair, the boss's work memory (at most 8,192 bytes; kept at 0x000EC000) is copied away before the run and put back
after it. So only ONE hero's script, the one the game itself hooked last, steps the boss's numbers: the time
limit runs as in the game and a press counts once. (The hero who presses becomes the first hero of the pair at
that moment, th_new, so each player's own press is the one that counts.)
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together9.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tk_run" in s:
    raise SystemExit("already there")
assert "tn_far" in s, "the eighth form must be there first"
a = s.index("th_tick:  ")
b = s.index("tg_tick:  ", a)
new = '''th_tick:                          # from 0x00177510 (the forty-third glue's jal hs_tick, or the game's runner): a hero's
    addiu sp,sp,-32               # hooked script runs. s0 = the hero, a0 = the script context
    sd ra,0(sp)
    sd zero,8(sp)
    lui t7,0x000E
    addiu t2,zero,1
    sw t2,0x7E48(t7)              # noted, so that tg_cap and th_new leave what it does alone
    lw t3,0x7E38(t7)
    bne t3,s0,tk_run              # not the second hero of a pair: as the game
    lw t4,52(a0)                  # the work memory (the boss's own: the hooked script shares it)
    beq t4,zero,tk_run
    lw t5,0(a0)                   # the program
    beq t5,zero,tk_run
    nop
    lw t5,16(t5)                  # its work size
    addiu t5,t5,3
    srl t5,t5,2
    sll t5,t5,2
    beq t5,zero,tk_run
    sltiu t2,t5,0x2001
    beq t2,zero,tk_run            # more than 8,192 bytes: not kept
    lui t6,0x000E
    ori t6,t6,0xC000              # the place the copy is kept
    sd t4,8(sp)
    sd t5,16(sp)
    addu t9,t4,t5
tk_c1:
    lw t2,0(t4)
    addiu t4,t4,4
    sw t2,0(t6)
    bne t4,t9,tk_c1
    addiu t6,t6,4
tk_run:
    jal HOOK_NEXT
    nop
    ld t4,8(sp)
    beq t4,zero,tk_done
    ld t5,16(sp)
    lui t6,0x000E
    ori t6,t6,0xC000
    addu t9,t4,t5
tk_c2:
    lw t2,0(t6)                   # the boss's numbers as they were before the second hero's copy ran
    addiu t6,t6,4
    sw t2,0(t4)
    addiu t4,t4,4
    bne t4,t9,tk_c2
    nop
tk_done:
    lui t7,0x000E
    sw zero,0x7E48(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
'''
s = s[:a] + new + s[b:]
x = "TG_END = 0x000EA800"
assert s.count(x) == 1
s = s.replace(x, "TG_END = 0x000EB000")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
