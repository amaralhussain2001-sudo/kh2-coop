"""One-off (tenth round, STATE part 129): THE LAUNCHER NAMES EACH PC BY ITS OWN COMPUTER NAME (the user: "make the automatic pc name";
before, the package carried the name saved on the first PC, "PC FORCE", and the launcher's default was the Windows account name).
make_test_package.py: (1) one more launcher edit: the default name $env:USERNAME -> $env:COMPUTERNAME; (2) the package's my-settings.txt
gets NO Name line, so each PC starts with its own computer name (the player can still type another; the launcher saves it).
The launcher is a program file: the package id changes. Run once:  python -I tools/package/edit_package_v22c.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "make_test_package.py"
t = p.read_text(encoding="utf-8")
if "COMPUTERNAME" in t:
    raise SystemExit("already there")
old = "EDITS = [\n"
assert t.count(old) == 1
t = t.replace(old, old + "    ('    $s = @{ Name = $env:USERNAME; ', '    $s = @{ Name = $env:COMPUTERNAME; '),   # each PC: its own computer name\n")
old = '    s.update({"Layout": "1", "Game": DISC_NAME, "Screen": "4:3", "Quality": QUALITY})\n'
assert t.count(old) == 1
t = t.replace(old, old + '    s.pop("Name", None)                                               # no saved name: each PC shows its own computer name\n')
p.write_text(t, encoding="utf-8", newline="\n")
print("make_test_package.py: computer name as the default name, no Name in my-settings.txt")
