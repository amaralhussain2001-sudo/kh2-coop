"""One-off: the header of tools/merge/merge_v7.py gets the description of the fiftieth glue as it is built now (the
text there still told the first experiment). No routine is changed: every build must come out bit for bit as before.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together12.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "FIFTIETH GLUE (built only with the option --together" in s:
    raise SystemExit("already there")
a = s.index("FIFTIETH GLUE, AN EXPERIMENT")
b = s.index("  python -I tools/merge/merge_v7.py [outDir]", a)
new = '''FIFTIETH GLUE (built only with the option --together; plan row 9, second half; the user's decision of 2026-11-10
"both heroes do a boss's scripted move together"): BOTH HEROES IN SHAN-YU'S CLASH.
Read in the program and in Shan-Yu's script (B_MU100):
 - the hero's side of a boss's move is a script that the boss's script HOOKS onto the hero (the script call
   trap_obj_hook = 0x00171FA8: a new context from 0x0016CF00(the boss's script, 0, function, [hero, extra], count),
   set on the hero with 0x00177460 = hero + 0xAEC, run once a step at 0x00177510). That hooked function makes
   the clash's captures on its hero (252, 253, 255, 254), offers "Press" / "Takedown" and counts the pushes;
 - a hooked context shares the boss's work memory (context + 16; + 52 is its handle); the boss's own numbers of
   the clash sit there (Shan-Yu: push count, push speed, time limit at work + 148, + 152, + 156) and the
   hero-side loop steps them.
The routines (0x000E9C00 ..; values 0x000E7E30 .. 0x000E7E48), all only in Shan-Yu's room (world 08, room 09):
 th_new (the call at 0x00171FE4): a PAIR is made when an enemy's script (not a hero's, not a helper's) hooks a
   script onto a hero and the hook is not the answer to a hero's own command: the other hero, when he is up,
   free (not held, no hooked script) and within 500 units, is put 55 units beside and 55 units behind the first
   (0x0016AF58 get direction, 0x0016ACE0 set position, 0x0016AEF0 set direction) and gets HIS OWN COPY of the
   hooked script. While the pair lives, every later hook on one of the two (the push, the takedown) is copied to
   the other as long as he is still in the move.
 th_tick (the call at 0x00177510): notes "a hero's hooked script runs" (0x000E7E48). When it is the script of the
   SECOND hero of the pair (the one who got the copy last), the boss's three numbers are kept before the run and
   put back after it: one script steps the boss's clock, and a press counts once (the hero who presses becomes
   the first hero at that moment).
 tg_cap (the jump at 0x00180378, the paired-move routine): a capture that the boss's OWN script makes on one hero
   of a living pair is copied to the other while he is still in the move (he is turned to the boss first).
   Without a pair nothing is copied: a grab or a lift (the falcon) stays that hero's alone.
 tg_tick (the call at 0x00138538): the pair is forgotten 10 steps after nobody is held and nobody has a hooked
   script. Safety rule: a hero of the pair who is held, has no hooked script and got no capture for 120 steps is
   freed ("no motion" 0x0017EFA0, then "go idle" 0x0016BD60(hero, 0)).
 tg_ro (0x00189E3C): a command offered by the boss's MOTION goes to both heroes of the pair.
 And the forty-seventh glue's rule "one object holds one hero" lets both heroes of a living pair press.
NOT together with the test recorders that sit on 0x00180378 (the kits -cap).

'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
