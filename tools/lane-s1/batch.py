"""Lane S1: run a list of jump-disc tests one after the other (build disc, run, delete disc).

  python -I tools/lane-s1/batch.py <batchfile>
Each non-empty line of the batch file (fields separated by '|'):
  test-name | disc name | build_disc arguments | frames | snap frames | probe frames | p1 spec | p2 spec | patch dir name | extra run_s1 arguments
'disc name' is the <name> for build_disc.py (disc = local/iso/test-s1-<name>.iso); the disc is built if missing and
deleted after the LAST line that uses it. Results: local/tests/<test-name>/; one line per test in
local/analysis/lane-s1/batch-<batchfile stem>.txt.
"""
import pathlib
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
py = sys.executable


def main():
    bf = pathlib.Path(sys.argv[1])
    rows = [[c.strip() for c in l.split("|")] for l in bf.read_text().splitlines() if l.strip() and not l.startswith("#")]
    res = ROOT / "local" / "analysis" / "lane-s1" / ("batch-" + bf.stem + ".txt")
    last_use = {}
    for i, r in enumerate(rows):
        last_use[r[1]] = i
    with open(res, "w", encoding="utf-8") as out:
        for i, r in enumerate(rows):
            r += [""] * (10 - len(r))
            test, disc, bargs, frames, snaps, probes, p1, p2, patch, extra = r[:10]
            iso = ROOT / "local" / "iso" / ("test-s1-%s.iso" % disc)
            if not iso.exists():
                b = subprocess.run([py, "-I", str(ROOT / "tools" / "lane-s1" / "build_disc.py"), disc] + shlex.split(bargs),
                                   capture_output=True, text=True)
                if b.returncode or not iso.exists():
                    out.write("%s: BUILD FAILED %s\n" % (test, (b.stderr or b.stdout)[-300:].replace("\n", " ")))
                    out.flush()
                    continue
            cmd = [py, "-I", str(ROOT / "tools" / "lane-s1" / "run_s1.py"), test, iso.name, "--frames", frames, "--snap", snaps,
                   "--p1", p1 or "ng;end:forever", "--p2", p2 or "end:forever",
                   "--patch", str(ROOT / "patches" / (patch or "merged-v2"))]
            if probes:
                cmd += ["--probe", probes]
            cmd += shlex.split(extra)
            t = subprocess.run(cmd, capture_output=True, text=True)
            line = " ; ".join(x.strip()[:200] for x in t.stdout.splitlines() if "session closed" in x or "screenshot pairs" in x or "OUT OF SYNC" in x or "TIMED" in x)
            out.write("%s: %s\n" % (test, line))
            out.flush()
            if last_use[disc] == i and iso.exists():
                iso.unlink()


if __name__ == "__main__":
    main()
