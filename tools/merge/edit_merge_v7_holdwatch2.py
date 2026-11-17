"""One-off: the SIXTIETH GLUE of tools/merge/merge_v7.py (--holdwatch) gets a TEST option, --holdwatch-test: the
limit is 100 steps instead of 1,800, so that ordinary holds of a boss are cut and the release itself ("no
motion", "go idle" on a hero a boss holds) can be seen in test runs (eighth round, part 82: the Groundshaker's
stuck moment did not come again in the run on candidate v93). Never in a build.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdwatch2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--holdwatch-test" in s:
    raise SystemExit("already there")
old = '''        labels, n = add_code(GY_AT, GY_END, GY_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "a hero in one and the same captured motion for 1,800 steps is let go")
'''
new = '''        gy_src = GY_SRC
        if "--holdwatch-test" in sys.argv:                                 # (test of the release itself: the limit is 100 steps)
            assert gy_src.count("slti t1,t4,%d" % GY_LIMIT) == 1
            gy_src = gy_src.replace("slti t1,t4,%d" % GY_LIMIT, "slti t1,t4,100")
        labels, n = add_code(GY_AT, GY_END, gy_src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "a hero in one and the same captured motion for 1,800 steps is let go")
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
