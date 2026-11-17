"""One-off (ninth round, STATE part 115): tools/own/row9_report.py, second build-21 edit: (1) the end of the last Xemnas's "Riku frees
Sora" part with one hero held IS seen in a test (run rs4 on v128, eh20 98: player 1's hero held in the part from 0x105 on, move 0x104
SENT BY PLAYER 1 at frame 17560, the part ended, the fight went on; in sync, "TLB misses 0"); (2) only an ENEMY's grab is single-target
(glue 65 fifth form, fifth part, candidate v129): a board or a gimmick (Mail Delivery, the skate challenges) keeps build 20's pair.
Then the report is made again by hand:
  python -I tools/own/edit_row9_build21b.py
  python -I tools/own/row9_report.py --xig=local/sweep/b15/row9-xig.txt --lux=local/sweep/b15/row9-lux.txt"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "tools" / "own" / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "SENT BY PLAYER 1 at frame 17560" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)


rep("THE END OF THE RIKU PART WITH ONE HERO HELD WAS NOT SEEN IN A TEST (it needs Riku steered to Xemnas: runs xsA, "
    "xsP, xsV, rkA .. rkE; for the user's playthrough).",
    "THE END OF THE RIKU PART WITH ONE HERO HELD IS SEEN: run rs4 on v128 (the rematch eh20 98): player 1's hero held "
    "from 0x105, Riku played by player 1, move 0x104 SENT BY PLAYER 1 at frame 17560, the part ended and the fight went "
    "on (in seven shorter runs a button script did not bring Riku to Xemnas).")
rep("""- The last Xemnas's "Riku frees Sora" part with ONE hero held (build 21): the held hero's player steers Riku; the
  part's END was not seen in a test (Riku must be steered to Xemnas). For the user's playthrough.""",
    """- (Seen 2026-11-15 night: the last Xemnas's "Riku frees Sora" part with ONE hero held ends by the held hero's
  player's own command, run rs4 eh20 98. How it feels to steer Riku is for the user's playthrough.)""")
rep("""Glue 65's fifth form (`--holdshared`) makes a pair only there; every other grab takes the hero the script names, as
the game; the stray-capture cure and the nets stay.""",
    """Glue 65's fifth form (`--holdshared`) makes a pair only there; every other ENEMY's grab takes the hero the script
names, as the game; the stray-capture cure and the nets stay. A captor that is no enemy (a board, a gimmick: Mail
Delivery, the skate challenges) keeps build 20's pair (its fifth part, candidate v129: the regression of v128 had 49
fault lines at those games' ends without it).""")
p.write_text(s, encoding="utf-8", newline="\n")
print("report source: build 21, second edit")
