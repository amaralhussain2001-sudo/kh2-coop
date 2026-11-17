"""One-off (ninth round, STATE part 117): tools/own/row9_report.py, third build-21 edit: the PLAYED column reads the runs of BUILD 21's
file v129 (tags rs5 = the 40 fights, h12 = the ten boss rooms), and section 3 names the captors that are no enemy and still take both
heroes (runs ob1 .. ob3 with tools/own/cap_log_probe3.py). Then the report is made again by hand:
  python -I tools/own/edit_row9_build21c.py
  python -I tools/own/row9_report.py --xig=local/sweep/b15/row9-xig.txt --lux=local/sweep/b15/row9-lux.txt"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "tools" / "own" / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "--tags=rs5,h12" in s:
    raise SystemExit("already there")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)


rep('"--json", "--tags=rs4,h11"]', '"--json", "--tags=rs5,h12"]')
rep('''"ON BUILD 21's CANDIDATES (v128 / v124), PLAYED ON PURPOSE WITH TWO HEROES: "''',
    '''"ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: "''')
rep("""Delivery, the skate challenges) keeps build 20's pair (its fifth part, candidate v129: the regression of v128 had 49
fault lines at those games' ends without it).""",
    """Delivery, the skate challenges) keeps build 20's pair (its fifth part, candidate v129: the regression of v128 had 49
fault lines at those games' ends without it). In the 40 fights on v129 such captors made pairs in three fights (runs ob1 ..
ob3 name them): the Storm Rider fight's whirlwinds (F_MU070_BOSS, kind G_OBJ, mu08 79) and moving parts of The World That
Never Was (F_EH070 / F_EH080 / F_EH110, kind F_OBJ, eh26 69 and eh28 68); every enemy there took only its target.""")
p.write_text(s, encoding="utf-8", newline="\n")
print("report source: build 21, third edit")
