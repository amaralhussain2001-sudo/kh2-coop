"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), seventh form (ninth round, STATE part 107).
READ: gq_inst writes its jumps into a FRESH flight module (its first words are still the game's), but it did not clear
the glue's own score-row values. A flight that ends without the score rows' free routine (a Game Over, a quit, a
module dropped) left them stale: row 2's state (0x000E7F68), its nine picture pointers (0x000E7F44 .. 0x7F64), the
gauge's digit (0x7F78) and the count of own picture places (0x7F98). The next flight then used stale pictures
(before the sixth form: pointers into the OLD module's heap) or, with the count at 10, took the heap again.
NOW: when gq_inst writes the jumps into a fresh module (a new flight: every old picture is gone with the old
module), it also clears 0x000E7F40 .. 0x000E7F7F and 0x000E7F98.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score8.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "a fresh module: the old pictures are gone" in s:
    raise SystemExit("already there")

old = '''@CHECKS@
@WRITES@
gqi_go:
    j GQ_NEXT
    nop
'''
assert s.count(old) == 1
s = s.replace(old, '''@CHECKS@
@WRITES@
    lui t7,0x000E                 # a fresh module: the old pictures are gone with the old module
    ori t6,t7,0x7F40
    addiu t5,zero,16
gqi_clr:
    sw zero,0(t6)                 # row 2 (0x7F40 .. 0x7F7F: its state, its pictures, the gauge's digit)
    addiu t5,t5,-1
    bne t5,zero,gqi_clr
    addiu t6,t6,4
    sw zero,0x7F98(t7)            # no own picture place is given out
gqi_go:
    j GQ_NEXT
    nop
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
