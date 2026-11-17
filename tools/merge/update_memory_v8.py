"""One-off: the memory files after test build 8 (2026-11-11 night)."""
import pathlib

BS = chr(92)
M = pathlib.Path("C:" + BS + "Users" + BS + "PC FORCE" + BS + ".claude" + BS + "projects" + BS
                 + "C--Users-PC-FORCE-Desktop-New-folder--3-" + BS + "memory")

m = M / "kh2-coop-ps2-project.md"
t = m.read_text(encoding="utf-8")
if "5b499fbc5f21" not in t:
    t = t.rstrip("\n") + "\n\n" + (
        "Night of 2026-11-11: test package BUILD 8, id 5b499fbc5f21, with a NEW DISC v4 "
        "(`local\\iso\\kh2-coop-v4.iso`, SHA-1 97e37dd9..., builder `tools\\merge\\build_disc_v4.py`, disc patch "
        "`kh2-coop-v4.kh2patch`: both players must make the \"TEST v4\" disc file). New: (1) a second skateboard "
        "beside every skateboard of the game (147 places) and the five skate challenges for two; (2) Donald and "
        "Goofy split up with the heroes (one helper each when the heroes are more than 900 units apart; the "
        "helpers are led by the game's \"follow\" system, whose leader is read at 0x00111E98); (3) a boss's "
        "scripted move shows on the screen of the player whose hero is in it, the other keeps his own camera; "
        "(4) Valor and Master Form tried for player 2. Validated by all suites and rehearsed. Known and NOT "
        "solved: the follow-up command of a boss move that grabbed player 2 sits in player 1's menu; in free "
        "roam the walking player's menu is drawn with the board frame while the other rides. The user asked for "
        "a hand-over prompt at the end of that session; the resume point is `docs\\STATE.md`, PICK UP HERE.\n")
    m.write_text(t, encoding="utf-8")

i = M / "MEMORY.md"
it = i.read_text(encoding="utf-8")
old = "builds (merged-v6, disc v3, test package 7, id 8d116c1087c7)"
assert it.count(old) == 1
i.write_text(it.replace(old, "builds (merged-v6, disc v4, test package 8, id 5b499fbc5f21)"), encoding="utf-8")

f = M / "take-recommended-and-continue.md"
ft = f.read_text(encoding="utf-8")
old = 'and then "finish all the tasks then i\'m going to test it one time after u finish everything".'
assert ft.count(old) == 1
if "prompt for next claude" not in ft:
    ft = ft.replace(old, old + ' Later on 2026-11-11, after my build 7 report listed four things as "not done", they '
                    'wrote "continue until u finish the not done tasks" and "after u finish all the tasks then i\'m going '
                    'to test it ( after all the tasks )"; near the end of that long session: "after finish the current '
                    'task prepare to clear and give me the promot for next claude so he continue all the tasks" (so: '
                    'when a session gets long, finish the task in hand, then hand over with a ready prompt; the next '
                    'session continues the list, it does not start over).')
    f.write_text(ft, encoding="utf-8")
print("memory updated")
