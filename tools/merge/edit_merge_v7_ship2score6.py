"""One-off: TWO TEST OPTIONS for the sixty-sixth glue of tools/merge/merge_v7.py (ninth round, STATE parts 103 to 106:
Gummi route 8 is flown differently since glue 66; run on v107 = build 19's numbers, so the glue is the cause).
To find WHICH HALF of the glue changes the flight:
  --gq-nodisp    the installer writes only the five counting jumps (a shot's start-up, a hit, a kill, the score's
                 add and reset); the second score row and the gauge's digit are not shown
  --gq-nocount   the installer writes only the four jumps and the one call of the score rows; nothing is counted
                 for player 2 (his row shows 0)
Both are TEST options: in the builder, in no build. Without them the builder's output does not change.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score6.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--gq-nodisp" in s:
    raise SystemExit("already there")

old = '''    checks, writes = "", ""
    for site, word0, name in GQ_SITES:
'''
assert s.count(old) == 1
s = s.replace(old, '''    checks, writes = "", ""
    sites, calls = GQ_SITES, GQ_CALLS
    if "--gq-nodisp" in sys.argv:                                          # TEST: the counting half only
        sites, calls = GQ_SITES[:5], ()
    if "--gq-nocount" in sys.argv:                                         # TEST: the score rows only
        sites = GQ_SITES[5:]
    for site, word0, name in sites:
''')
old = '''    for site, word0, name in GQ_CALLS:
        hi = (site + 0x8000) >> 16'''
assert s.count(old) == 1
s = s.replace(old, '''    for site, word0, name in calls:
        hi = (site + 0x8000) >> 16''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
