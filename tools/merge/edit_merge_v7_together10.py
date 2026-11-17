"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue), TENTH form.
The ninth form put the boss's WHOLE work memory back after the second hero's hooked script had run. Runs tg25 and
tg26 (candidate v72): the clash's timing was the game's again (490 frames, seven pushes) and the fight was won,
BUT 50 fault lines each, from the end of the first clash on (pc 0x00187E34, 0x00186CE8, 0x00171DA0, 0x001880B0: a
script call with a number where the boss's object should be). Putting back everything also threw away what the
second hero's script must leave behind (at the end of the clash it starts the boss's next act).
Now only THE THREE NUMBERS that must not be stepped twice are kept and put back: the words at work + 148, + 152,
+ 156 (Shan-Yu's push count, push speed and time limit; READ in his script: the fields 144, 148, 152 of the record
at work + 4). Everything else the second hero's script writes stays, as in the seventh form (candidate v70), which
had no fault line in nine runs.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together10.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tk_keep" in s:
    raise SystemExit("already there")
assert "tk_run" in s, "the ninth form must be there first"
a = s.index("th_tick:  ")
b = s.index("tg_tick:  ", a)
new = '''th_tick:                          # from 0x00177510 (the forty-third glue's jal hs_tick, or the game's runner): a hero's
    addiu sp,sp,-48               # hooked script runs. s0 = the hero, a0 = the script context
    sd ra,0(sp)
    sd zero,8(sp)
    lui t7,0x000E
    addiu t2,zero,1
    sw t2,0x7E48(t7)              # noted, so that tg_cap and th_new leave what it does alone
    lw t3,0x7E38(t7)
    bne t3,s0,tk_run              # not the second hero of a pair: as the game
    lw t4,52(a0)                  # the work memory (the boss's own: the hooked script shares it)
    beq t4,zero,tk_run
    nop
tk_keep:
    sd t4,8(sp)                   # the boss's three numbers of the clash (Shan-Yu: push count, push speed, time limit)
    lw t2,148(t4)
    sw t2,16(sp)
    lw t2,152(t4)
    sw t2,20(sp)
    lw t2,156(t4)
    sw t2,24(sp)
tk_run:
    jal HOOK_NEXT
    nop
    ld t4,8(sp)
    beq t4,zero,tk_done
    lw t2,16(sp)
    sw t2,148(t4)                 # as they were before the second hero's copy ran: one script steps them
    lw t2,20(sp)
    sw t2,152(t4)
    lw t2,24(sp)
    sw t2,156(t4)
tk_done:
    lui t7,0x000E
    sw zero,0x7E48(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
