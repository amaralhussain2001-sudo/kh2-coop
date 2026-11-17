"""One-off: the SIXTY-SECOND GLUE of tools/merge/merge_v7.py (--ownitems), third form (ninth round, part 90).
Found with the recorder at the refill routine 0x00188AC8 (run rf1): the game fills empty item places EVERY STEP
while there is no fight, by a jump at the end of the fight watcher (0x001918A8: j 0x001A3710), not only from the
pause menu (0x00253BDC). So player 2's places were filled only when a pause menu opened. The jump goes through
oi_refill too.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownitems3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "0x001918A8" in s:
    raise SystemExit("already there")
a = '''        hook_game(0x00253BDC, jal(0x001A3710), jal(labels["oi_refill"]), "the game fills empty places: the other player's too, from his own stock")
'''
assert s.count(a) == 1
b = a + '''        hook_game(0x001918A8, jmp(0x001A3710), jmp(labels["oi_refill"]), "the same, each step while there is no fight (the fight watcher's jump)")
'''
s = s.replace(a, b)
a = "        n_glue += n + 6" + NL
assert s.count(a) == 1
s = s.replace(a, "        n_glue += n + 7" + NL)
a = "fills the other player's places from his own stock (0x00253BDC); oi_swap"
assert s.count(a) == 1
s = s.replace(a, "fills the other player's places from his own stock (0x00253BDC and, each step without a fight, 0x001918A8); oi_swap")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
