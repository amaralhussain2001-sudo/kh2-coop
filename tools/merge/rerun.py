"""Print (or run) the command that repeats an earlier merge-lane test with another patch folder.

Reads the old test's session files in local/tests/<old>/ (disc, players, frames, screenshot frames, scripts, what
the pads do after the script, speed) and calls tools/merge/mrun.sh with a new name and patch folder.

  python -I tools/merge/rerun.py <old-test> <new-test> <patchDir|-> [--disc NAME.iso] [--run] [--recorder]
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def ini(path):
    d = {}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def main():
    old, new, pdir = sys.argv[1], sys.argv[2], sys.argv[3]
    t = ROOT / "local" / "tests" / old
    s1 = ini(t / "session_p1.ini")
    players = int(s1.get("Players", "1"))
    s2 = ini(t / "session_p2.ini") if players > 1 and (t / "session_p2.ini").exists() else {}
    summary = (t / "summary.txt").read_text(errors="replace") if (t / "summary.txt").exists() else ""
    m = re.search(r"disc (.+?\.iso), ", summary)
    disc = m.group(1) if m else "?"
    if "--disc" in sys.argv:
        disc = sys.argv[sys.argv.index("--disc") + 1]
    m = re.search(r"speed ([0-9.]+)", summary)
    speed = m.group(1) if m else "2"
    then = s1.get("BotThen", s1.get("Bot", "idle"))
    if then not in ("idle", "random"):
        then = "idle"
    p1 = s1.get("Script", "")
    p2 = s2.get("Script", "") or "-"
    runner = "mrecrun.sh" if "--recorder" in sys.argv else "mrun.sh"
    cmd = ["bash", str(ROOT / "tools" / "merge" / runner).replace("\\", "/"), new, disc, s1.get("ExitAtFrame", "6000"),
           speed, s1.get("SnapFrames", ""), str(players), p1.replace("\\", "/"), p2.replace("\\", "/"), then,
           pdir.replace("\\", "/")]
    print(" ".join('"%s"' % c if " " in c else c for c in cmd))
    if "--run" in sys.argv:
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout[-1500:])
        if r.returncode:
            print(r.stderr[-800:])


if __name__ == "__main__":
    main()
