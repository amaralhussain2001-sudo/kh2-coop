"""One-off (tenth round, STATE part 128): THE CONTROLLER FIX GOES INTO THE TEST PACKAGE (the user: "yes add the controller fix and paste
it again"). make_test_package.py copies the emulator settings PCSX2.ini from Desktop\PS2-ONLINE (never changed by this project), so the
fix is a step after that copy: tools/package/xinput_fix.py (XInput route on + controller port 1 also on the first XInput pad). The
same step is applied now to the finished package in dist (its id does not change: emulator\inis is not a program file).
  python -I tools/package/edit_package_v22b.py          (run ONCE)"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from xinput_fix import add_xinput  # noqa: E402

p = HERE / "make_test_package.py"
t = p.read_text(encoding="utf-8")
if "add_xinput" in t:
    raise SystemExit("already there")
old = '    shutil.copy2(SRC / "emulator" / "inis" / "PCSX2.ini", emu / "inis" / "PCSX2.ini")  # the user\'s own controls\n'
assert t.count(old) == 1
new = old + ('    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
             '    from xinput_fix import add_xinput                                 # the controller fix (STATE part 128)\n'
             '    add_xinput(emu / "inis" / "PCSX2.ini")\n')
t = t.replace(old, new)
p.write_text(t, encoding="utf-8", newline="\n")
print("make_test_package.py: the controller fix after the copy of PCSX2.ini")
ini = HERE.parent.parent / "dist" / "PS2-ONLINE-KH2-TEST" / "emulator" / "inis" / "PCSX2.ini"
print("dist PCSX2.ini: XInput-0 bindings added:", add_xinput(ini))
