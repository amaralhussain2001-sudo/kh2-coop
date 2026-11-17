"""One-off (ninth round, STATE part 117): the read-me of TEST BUILD 21, corrected after the 40 fights on the packaged candidate v129
(tag rs5) and their captors (runs ob1 .. ob3, `tools/own/cap_log_probe3.py`): besides the last Xemnas's laser part, the moves of
things that are NO ENEMY take both heroes, as in build 20: the whirlwinds of the Storm Rider fight (F_MU070_BOSS, kind G_OBJ) and
moving parts of The World That Never Was (F_EH070 / F_EH080 / F_EH110, kind F_OBJ); also the skateboards and Mail Delivery. An
enemy's grab takes only its target. Only the read-me changes (the patch files and the disc do not).
  python -I tools/package/edit_package_v21b.py          (run ONCE, then make_test_package.py --rebuild and finish_two_pcs.py)"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = README.read_text(encoding="utf-8")
if "THAT IS NO ENEMY" in t:
    raise SystemExit("already done")
PAIRS = [
    ("""(4) A BOSS'S GRAB TAKES ONLY THE HERO IT IS AIMED AT AGAIN; the other player keeps fighting. Only the last
    Xemnas's laser part takes both heroes, and there each player has his own "Reflect". Each player keeps his
    own controller in a hold. Read "BOSSES THAT HOLD A HERO" further down.""",
     """(4) AN ENEMY'S GRAB TAKES ONLY THE HERO IT IS AIMED AT AGAIN; the other player keeps fighting. Shared moves
    take both heroes: the last Xemnas's laser part (there each player has his own "Reflect"), and, as before, the
    moves of a thing THAT IS NO ENEMY (the whirlwinds in the Storm Rider fight, moving parts of The World That
    Never Was, the skateboards). Each player keeps his own controller in a hold. Read "BOSSES THAT HOLD A HERO"
    further down."""),
    ("""  BUILD 21 IT TAKES THE HERO IT IS AIMED AT AGAIN (only the last Xemnas's laser part takes both): read "BOSSES""",
     """  BUILD 21 AN ENEMY'S GRAB TAKES THE HERO IT IS AIMED AT AGAIN (shared moves take both): read "BOSSES"""),
    ("""  ONE SHARED MOVE TAKES BOTH HEROES: the last Xemnas's laser part at the end (the game itself puts the player
  and Riku into it).""",
     """  SHARED MOVES TAKE BOTH HEROES. The last Xemnas's laser part at the end (the game itself puts the player and
  Riku into it). And, as in build 20, the moves of a thing that is no enemy: the whirlwinds that lift the heroes
  in the Storm Rider fight, moving parts of The World That Never Was, the skateboards and Mail Delivery: both
  heroes go along. In the laser part"""),
    ("""  Riku into it). And, as in build 20, the moves of a thing that is no enemy: the whirlwinds that lift the heroes
  in the Storm Rider fight, moving parts of The World That Never Was, the skateboards and Mail Delivery: both
  heroes go along. In the laser part Both heroes stand in it and""",
     """  Riku into it). And, as in build 20, the moves of a thing that is no enemy: the whirlwinds that lift the heroes
  in the Storm Rider fight, moving parts of The World That Never Was, the skateboards and Mail Delivery: both
  heroes go along. In the laser part both heroes stand together and"""),
]
for old, new in PAIRS:
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)
README.write_text(t, encoding="utf-8")
print("read-me: shared moves corrected")
