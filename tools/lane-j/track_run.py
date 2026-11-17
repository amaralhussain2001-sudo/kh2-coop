"""Lane J: build a jump disc, run it once, and follow the player-type objects through PINE (read-only) so that
"is the twin really there, and where?" has a number for an answer, not only a screenshot.

  python -I tools/lane-j/track_run.py <name> <frames> <snap,frames> -- <build_disc.py arguments after the name>

Writes local/tests/j-<name>/track.txt (output of tools/lane-b/track.py: one line whenever the room, the HP or a
rounded position of a player-type object changes) and the usual screenshots and sheet. The disc is deleted.
"""
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PINE = os.environ.get("J_PINE", "28091")


def main():
    argv = sys.argv[1:]
    cut = argv.index("--")
    name, frames, snaps = argv[:3]
    build = argv[cut + 1:]
    py = sys.executable
    if subprocess.run([py, "-I", str(ROOT / "tools" / "lane-j" / "build_disc.py"), name] + build).returncode:
        sys.exit("build failed")
    iso = ROOT / "local" / "iso" / f"test-j-{name}.iso"
    test = "j-" + name
    out = ROOT / "local" / "tests" / test
    cmd = [py, "-I", str(ROOT / "tools" / "kh2_session.py"), "run", test, "--iso", str(iso),
           "--run-dir", os.environ.get("J_RUN_DIR", "run-j"), "--port", os.environ.get("J_PORT", "29150"),
           "--players", "1", "--slots", "0", "--frames", frames, "--speed", "2", "--snap", snaps,
           "--script", str(ROOT / "tests" / "scripts" / "lane-j" / "j_probe.txt"), "--fresh-card", "--pine", PINE,
           "--timeout", "300", "--tail", "2"]
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(8)
    secs = str(int(int(frames) / 120) + 10)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "track.txt", "w") as f:
        subprocess.run([py, "-I", str(ROOT / "tools" / "lane-b" / "track.py"), PINE, secs, "--step", "40"], stdout=f, stderr=subprocess.STDOUT)
    print(run.communicate()[0][-600:])
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "tools" / "contact_sheet.ps1"),
                    "-Dir", str(out), "-Pattern", "p1_f*.png", "-Out", str(out / "sheet.png"), "-Cols", "4", "-Width", "480"])
    if iso.exists():
        iso.unlink()
    lines = (out / "track.txt").read_text(errors="replace").splitlines()
    print("track lines:", len(lines))
    for l in lines[:2] + lines[-3:]:
        print("  ", l[:230])


if __name__ == "__main__":
    main()
