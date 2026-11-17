"""Lane J: run a list of look-tests one after another (one emulator at a time), each with its own log file.

  python -I tools/lane-j/batch.py <batch-name> <list-file>

list-file lines:  <test-name> | <script> | <frames> | <snap frames> | <build_disc.py arguments> [| extra run_form options]
Logs: local/j-<batch-name>/<test-name>.txt ; summary printed at the end.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
name, listfile = sys.argv[1], sys.argv[2]
logdir = ROOT / "local" / ("j-" + name)
logdir.mkdir(parents=True, exist_ok=True)
rows = []
for line in pathlib.Path(listfile).read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = [p.strip() for p in line.split("|")]
    test, script, frames, snaps, build = parts[:5]
    extra = parts[5].split() if len(parts) > 5 and parts[5] else []
    cmd = [sys.executable, "-I", str(ROOT / "tools" / "lane-j" / "run_form.py"), test, str(ROOT / script), frames, snaps,
           "--peek", "0032BAE0,0032BAE4,01C6C750,01C61958"] + extra + ["--"] + build.split()
    # arguments with spaces are written with '_' in the list file: --jump NM_51 -> "NM 51"
    cmd = [c.replace("_", " ") if i > 0 and cmd[i - 1] in ("--jump", "--jump1") else c for i, c in enumerate(cmd)]
    with open(logdir / (test + ".txt"), "w") as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    text = (logdir / (test + ".txt")).read_text(errors="replace")
    state = "TIMED OUT" if "TIMED OUT" in text else "closed" if "session closed" in text else "build failed" if "build failed" in text else "?"
    peek = ""
    plog = ROOT / "local" / "tests" / ("j-" + test) / "p1.log"
    if plog.exists():
        pk = [l for l in plog.read_text(errors="replace").splitlines() if "peek:" in l]
        peek = pk[-1].split("peek:")[1].strip() if pk else ""
    rows.append(f"{test}: {state}; {peek}")
print("\n".join(rows))
