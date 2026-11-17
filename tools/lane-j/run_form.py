"""Lane J: build one jump disc, run one scripted test on it, make a contact sheet, optionally delete the disc.

  python -I tools/lane-j/run_form.py <name> <script> <frames> <snap,frames> [--keep] [--patch-dir DIR] [--peek HEX,..]
         [--players N] [--script2 FILE] -- <build_disc.py arguments after the name>

Test folder: local/tests/j-<name>/ (sheet.png). Disc: local/iso/test-j-<name>.iso (deleted unless --keep).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def main():
    argv = sys.argv[1:]
    cut = argv.index("--")
    mine, build = argv[:cut], argv[cut + 1:]
    name, script, frames, snaps = mine[:4]
    keep = "--keep" in mine
    opt = {}
    for key in ("--patch-dir", "--peek", "--players", "--script2", "--speed", "--testname", "--timeout"):
        if key in mine:
            opt[key] = mine[mine.index(key) + 1]
    py = sys.executable
    r = subprocess.run([py, "-I", str(ROOT / "tools" / "lane-j" / "build_disc.py"), name] + build)
    if r.returncode:
        sys.exit("build failed")
    iso = ROOT / "local" / "iso" / f"test-j-{name}.iso"
    test = opt.get("--testname", "j-" + name)
    players = opt.get("--players", "1")
    import os
    # a second set of emulator copies can run another batch at the same time: J_RUN_DIR=run-j2 J_PORT=29170
    cmd = [py, "-I", str(ROOT / "tools" / "kh2_session.py"), "run", test, "--iso", str(iso), "--run-dir", os.environ.get("J_RUN_DIR", "run-j"),
           "--port", os.environ.get("J_PORT", "29150"), "--players", players, "--slots", "0" if players == "1" else "0,1", "--frames", frames,
           "--speed", opt.get("--speed", "4"), "--snap", snaps, "--script", script, "--fresh-card", "--timeout", opt.get("--timeout", "400"), "--tail", "2"]
    if "--script2" in opt:
        cmd += ["--script2", opt["--script2"]]
    if "--patch-dir" in opt:
        cmd += ["--patch-dir", opt["--patch-dir"]]
    if "--peek" in opt:
        cmd += ["--peek", opt["--peek"]]
    subprocess.run(cmd)
    out = ROOT / "local" / "tests" / test
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "tools" / "contact_sheet.ps1"),
                    "-Dir", str(out), "-Pattern", "p1_f*.png", "-Out", str(out / "sheet.png"), "-Cols", "4", "-Width", "480"])
    if not keep and iso.exists():
        iso.unlink()
        print("disc deleted (recipe kept in local/variants/j-" + name + ")")


if __name__ == "__main__":
    main()
