"""Lane S1: run one two-player test on a disc with the merged patch, probe it, make a contact sheet.

  python -I tools/lane-s1/run_s1.py <test> <iso-name-in-local/iso> --frames N --snap a,b,c
         --p1 "<spec>" --p2 "<spec>" [--then idle|random] [--patch DIR] [--probe a,b,c] [--raw HEX:LEN,...]
         [--speed 4] [--players 2] [--peek HEX,...] [--cols 4] [--width 480] [--timeout 500]

Button specs (items separated by ';'), turned into script files in tests/scripts/lane-s1/<test>_p1.txt / _p2.txt:
  ng                    the six Circle presses that start a New Game (frames 3000..3600)
  press:BTNS:frame      one 4-frame press, e.g. press:TRI:5000 or press:LX=255 O:5000
  hold:BTNS:frame:n     hold for n frames
  mash:BTNS:f0:f1:step  a 4-frame press every <step> frames from f0 to f1
  end:frame             last line (after it the harness's --then mode applies); 'forever' = never ends (stays idle)
  random                (whole spec) no script: random buttons from frame 0
Test output: local/tests/<test>/ (pictures, logs, probe.txt, sheet.png, summary.txt).
"""
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCR = ROOT / "tests" / "scripts" / "lane-s1"


def make_script(spec, path):
    lines = ["# made by tools/lane-s1/run_s1.py from: " + spec]
    for item in [x.strip() for x in spec.split(";") if x.strip()]:
        part = item.split(":")
        if part[0] == "ng":
            lines += ["%d 4 O" % f for f in (3000, 3120, 3240, 3360, 3480, 3600)]
        elif part[0] == "press":
            lines.append("%d 4 %s" % (int(part[2]), part[1]))
        elif part[0] == "hold":
            lines.append("%d %d %s" % (int(part[2]), int(part[3]), part[1]))
        elif part[0] == "mash":
            for f in range(int(part[2]), int(part[3]), int(part[4])):
                lines.append("%d 4 %s" % (f, part[1]))
        elif part[0] == "end":
            lines.append("%d 1 " % (999999 if part[1] == "forever" else int(part[1])))
        else:
            sys.exit("bad spec item: " + item)
    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("test")
    ap.add_argument("iso")
    ap.add_argument("--frames", type=int, required=True)
    ap.add_argument("--snap", required=True)
    ap.add_argument("--p1", default="ng;end:forever")
    ap.add_argument("--p2", default="end:forever")
    ap.add_argument("--then", default="idle")
    ap.add_argument("--patch", default=str(ROOT / "patches" / "merged-v2"))
    ap.add_argument("--probe", default="")
    ap.add_argument("--raw", default="")
    ap.add_argument("--speed", default="4")
    ap.add_argument("--players", default="2")
    ap.add_argument("--peek", default="")
    ap.add_argument("--cols", default="4")
    ap.add_argument("--width", default="480")
    ap.add_argument("--timeout", default="500")
    ap.add_argument("--port", default="29750")
    ap.add_argument("--pine", default="28151")
    ap.add_argument("--run-dir", default="run-s1")
    ap.add_argument("--rc", default="", help="START:END frames for the dense Reaction Command timeline (s1rc.py)")
    ap.add_argument("--rc-redirect", action="store_true", help="ONE-copy tests only: s1rc.py --redirect")
    a = ap.parse_args()

    SCR.mkdir(parents=True, exist_ok=True)
    out = ROOT / "local" / "tests" / a.test
    if out.exists():
        for f in out.glob("*"):
            if f.is_file():
                f.unlink()
    iso = ROOT / "local" / "iso" / a.iso
    py = sys.executable
    cmd = [py, "-I", str(ROOT / "tools" / "kh2_session.py"), "run", a.test, "--iso", str(iso), "--run-dir", a.run_dir,
           "--port", a.port, "--players", a.players, "--slots", "0" if a.players == "1" else "0,1",
           "--frames", str(a.frames), "--speed", a.speed, "--snap", a.snap, "--fresh-card", "--timeout", a.timeout,
           "--tail", "3", "--then", a.then, "--pine", a.pine]
    if a.patch and a.patch != "-":
        cmd += ["--patch-dir", a.patch]
    if a.peek:
        cmd += ["--peek", a.peek]
    if a.p1 == "random":
        cmd += ["--bot", "random"]
    else:
        s1 = SCR / (a.test + "_p1.txt")
        make_script(a.p1, s1)
        cmd += ["--script", str(s1)]
    if a.players != "1":
        if a.p2 == "random":
            if a.p1 == "random":
                pass
            else:
                cmd += ["--bot", "random"]
        else:
            s2 = SCR / (a.test + "_p2.txt")
            make_script(a.p2, s2)
            cmd += ["--script2", str(s2)]
    hlog = open(ROOT / "local" / "analysis" / "lane-s1" / (a.test + "-harness.txt"), "w")
    h = subprocess.Popen(cmd, stdout=hlog, stderr=subprocess.STDOUT)
    pr = None
    if a.probe:
        pcmd = [py, "-I", str(ROOT / "tools" / "lane-s1" / "s1probe.py"), str(out), a.pine, a.probe, "--timeout", a.timeout]
        if a.raw:
            pcmd += ["--raw", a.raw]
        plog = open(ROOT / "local" / "analysis" / "lane-s1" / (a.test + "-probe-console.txt"), "w")
        pr = subprocess.Popen(pcmd, stdout=plog, stderr=subprocess.STDOUT)
    rc = None
    if a.rc:
        r0, r1 = a.rc.split(':')
        rcmd = [py, '-I', str(ROOT / 'tools' / 'lane-s1' / 's1rc.py'), str(out), a.pine, r0, r1, '--timeout', a.timeout]
        if a.rc_redirect:
            assert a.players == '1', 'the redirect write is for one-copy tests only'
            rcmd.append('--redirect')
        rlog = open(ROOT / 'local' / 'analysis' / 'lane-s1' / (a.test + '-rc-console.txt'), 'w')
        rc = subprocess.Popen(rcmd, stdout=rlog, stderr=subprocess.STDOUT)
    h.wait()
    if rc is not None:
        try:
            rc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            rc.kill()
    if pr is not None:
        try:
            pr.wait(timeout=20)
        except subprocess.TimeoutExpired:
            pr.kill()
    hlog.close()
    # keep the emulator logs of this run (the next run overwrites them): crashes are only visible there
    import shutil
    for n in ('p1', 'p2'):
        src = ROOT / 'local' / a.run_dir / n / 'logs' / 'emulog.txt'
        if src.exists():
            shutil.copyfile(src, out / ('emulog_%s.txt' % n))
    text = (ROOT / "local" / "analysis" / "lane-s1" / (a.test + "-harness.txt")).read_text(errors="replace")
    keep = [l for l in text.splitlines() if l.startswith("test ") or "session closed" in l or "OUT OF SYNC" in l or "TIMED" in l]
    print("\n".join(l[:230] for l in keep))
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "tools" / "contact_sheet.ps1"),
                    "-Dir", str(out), "-Pattern", "p1_f*.png", "-Out", str(out / "sheet.png"), "-Cols", a.cols, "-Width", a.width])
    # are the two copies' pictures identical?
    import hashlib
    same = diff = 0
    for f in sorted(out.glob("p1_f*.png")):
        g = out / f.name.replace("p1_", "p2_")
        if g.exists():
            if hashlib.sha1(f.read_bytes()).digest() == hashlib.sha1(g.read_bytes()).digest():
                same += 1
            else:
                diff += 1
    print("screenshot pairs: %d identical, %d different" % (same, diff))


if __name__ == "__main__":
    main()
