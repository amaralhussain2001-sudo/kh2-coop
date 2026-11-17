"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, FOURTH PART, FOURTH FORM (option --holdshared): ip_one IS TAKEN OUT AGAIN; hs_rc
STAYS (ninth round, the user's items 1 and 4 of 2026-11-15 evening; STATE part 113).
WHY: run xs3 on v127 (presses five frames apart; XEMNAS NAMED PLAYER 2'S HERO): the dome's own piece on the named hero
(routine 16000, hooked at the dome's start) asks "is my hero the player" (script call 1,309); ip_one answered "no" for
player 2's hero, so that piece let him go ("motion start 0") at counter 8284; with the named hero out of the dome the boss
stopped offering "Reflect", no reflect was made and the dome failed (player 1's hero hung in laser hits).
WHY ip_one IS NOT NEEDED: with hs_rc every reflect piece (routine 8874) goes onto player 1's hero (a press of player 2's hero
is sent in player 1's hero's name), and the lasers hit only player 1's hero, the engine's player (every dome run: xsI ..
xs6, named P1 or P2). So player 2's hero never carries a piece that can end the dome (L7175 -> L7213); the end runs once.
NOW: ip_one and its table word (0x0034E6A8, the script call 1,309) are taken out: the game's own routine again.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared8.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "ip_one" not in s:
    raise SystemExit("already done")


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("""0x001E2AC0; xsY: pieces on the named player 2 while the lasers hit player 1 failed the dome): hs_rc sends a press of
player 2's hero in player 1's hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press), and ip_one (script call 1,309) answers "not the player" for player 2's hero while he is held in the pair.
""", """0x001E2AC0; xsY: pieces on the named player 2 while the lasers hit player 1 failed the dome): hs_rc sends a press of
player 2's hero in player 1's hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press). The script call "is the player" stays the game's (a first safety net there let the named player 2 go: run xs3).
""")

i = s.index("ip_one:                           # the script call (1,309)")
j = s.index("ip_out:\n", i)
j = s.index('"""\n', j)
seg = s[i:j]
assert seg.count("addiu sp,sp,32") == 1 and seg.rstrip().endswith("addiu sp,sp,32"), seg[-80:]
s = s[:i] + s[j:]

rep('''            hook_game(0x0034E6A8, 0x00171090, labels["ip_one"], "the script call (1,309) 'is the player': not player 2's hero while he is held in the pair")
            n_glue += 1
''', '')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
