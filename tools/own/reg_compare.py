"""Read the whole regression's logs (tools/own/reg_par8.sh) and compare them with a saved regression.
  python -I tools/own/reg_compare.py <newPrefix> <newCountName> <oldDir> <oldPrefix> <oldCountName> [--save <dir>]
    python -I tools/own/reg_compare.py b22 w22 local/reg-b21 b21 w21 --save local/reg-b22
What it prints: for each of the fourteen logs the number of result lines ("session closed ..."), every result
line that is OUT OF SYNC, TIMED OUT or has a fault line count that is not 0, and every line that is not word for
word the old one (old and new shown). The one-hero control's picture check numbers are compared too.
--save copies the new logs into <dir> under the names the old ones have (the next regression writes over them)."""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
L = ROOT / "local"
new_p, new_c, old_dir, old_p, old_c = sys.argv[1:6]
old_dir = ROOT / old_dir
save = ROOT / sys.argv[sys.argv.index("--save") + 1] if "--save" in sys.argv else None
PAIRS = [  # (new file, old file name in the saved folder)
    (L / "m6-suite.log", "m6-suite.log"),
    (L / "m5s-suite.log", "m5s-suite.log"),
    (L / "b12-solo-nn.log", "b12-solo-nn.log"),
    (L / "own-batch7.log", "own-batch7.log"),
    (L / ("%s-batch.log" % new_p), "%s-batch.log" % old_p),
    (L / "final-b9-a.log", "final-b9-a.log"),
    (L / "final-b9-b.log", "final-b9-b.log"),
    (L / "final-b10.log", "final-b10.log"),
    (L / "final-b11.log", "final-b11.log"),
    (L / "final-b12-a.log", "final-b12-a.log"),
    (L / "final-b12-b.log", "final-b12-b.log"),
    (L / "final-b12-c.log", "final-b12-c.log"),
    (L / "sweep" / ("gummi-%s-a.log" % new_p), "gummi-%s-a.log" % old_p),
    (L / "sweep" / ("gummi-%s-b.log" % new_p), "gummi-%s-b.log" % old_p),
    (L / "sweep" / "b15" / ("count-%s.txt" % new_p), "counting-%s.txt" % old_c),
]
RES = re.compile(r"ession closed|OUT OF SYNC|TIMED OUT|refused")
TLB = re.compile(r"TLB misses (\d+)")


def norm(line, pref, cname):
    """One line without the things that differ from run to run: the prefix names, the harness's own clock in
    front of "session closed", the patch folder's name and word count."""
    line = line.rstrip().replace(pref, "@P@").replace(cname, "@C@")
    line = re.sub(r"^\d{6,} (session closed)", r"", line)
    line = re.sub(r"patches/[\w-]+( \(\d+ words\))?", "patches/@X@", line)
    line = re.sub(r"\d\d:\d\d:\d\d", "@T@", line)
    line = re.sub(r"test-own-v\d+\w*|test-v\d+-\w+", "@X@", line)
    return line


def near(x, y):
    """The same line but for a closing frame or a digest count that differs by one or two."""
    nx, ny = re.findall(r"\d+", x), re.findall(r"\d+", y)
    if re.sub(r"\d+", "#", x) != re.sub(r"\d+", "#", y) or len(nx) != len(ny):
        return False
    return all(abs(int(i) - int(j)) <= 2 for i, j in zip(nx, ny)) and ("closed at frame" in x or "digests" in x)


total, bad, diff_files = 0, 0, 0
for new, old_name in PAIRS:
    old = old_dir / old_name
    if not new.exists():
        print("MISSING new log:", new)
        bad += 1
        continue
    nl = new.read_text(encoding="utf-8", errors="replace").splitlines()
    ol = old.read_text(encoding="utf-8", errors="replace").splitlines() if old.exists() else []
    res = [l for l in nl if RES.search(l)]
    total += len(res)
    flagged = []
    for l in res:
        if "OUT OF SYNC" in l or "TIMED OUT" in l or "refused" in l or "never out of sync" not in l:
            flagged.append(l)
        elif any(int(n) for n in TLB.findall(l)):
            flagged.append(l)
    # fault line counts that stand on their own lines (the suites print them after the result line)
    for l in nl:
        if not RES.search(l) and any(int(n) for n in TLB.findall(l)):
            flagged.append(l)
    a = [norm(l, new_p, new_c) for l in nl]
    b = [norm(l, old_p, old_c) for l in ol]
    if new.name.startswith("count-"):                 # two lanes write this file at once: the order of the lines is chance
        a, b = sorted(a), sorted(b)
    same = a == b
    print("%-22s %3d result lines, %d flagged, %s" % (new.name, len(res), len(flagged),
                                                      "word for word as before" if same else "DIFFERENT from before (%d / %d lines)" % (len(a), len(b))))
    for l in flagged:
        print("    FLAG: " + l[:230])
        bad += 1
    if not same:
        n, close = 0, 0
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else "(no line)"
            y = b[i] if i < len(b) else "(no line)"
            if x != y and near(x, y):
                close += 1
            elif x != y:
                n += 1
                if n <= 12:
                    print("    line %d  new: %s" % (i + 1, x[:210]))
                    print("    line %d  old: %s" % (i + 1, y[:210]))
        if n > 12:
            print("    ... and %d more lines that differ" % (n - 12))
        if n:
            diff_files += 1
        print("    (%d lines differ by one or two in a closing frame or a digest count; %d lines differ otherwise)" % (close, n))
    if save:
        save.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(new, save / old_name.replace(old_p, new_p).replace(old_c, new_c))
if save:
    shutil.copyfile(L / "reg-par8.log", save / "reg-par8.log")
    print("saved to", save)
print("TOTAL: %d result lines, %d flagged lines, %d of %d logs differ from the saved regression" % (total, bad, diff_files, len(PAIRS)))
