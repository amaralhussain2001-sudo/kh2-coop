"""Same-file check tests for the test package, on the two rehearsal copies (local/kit-test-t/A = host, B = friend).

The host has the two-player disc. The friend has ANOTHER file of exactly the same size (and the same disc id).
  code : the friend joins with the join code      -> the launcher must refuse and say why; no emulator starts
  ip   : the friend joins by IP (no code, no tag) -> the emulator's own join check must refuse

  python -I tools/lane-t/mismatch.py <name> code|ip --host-game "<file>" --friend-game "<file>"
Results: local/tests/<name>/summary.txt
"""
import argparse
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("rehearse", ROOT / "tools" / "lane-t" / "rehearse.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
KIT = R.KIT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("mode", choices=["code", "ip"])
    ap.add_argument("--host-game", required=True)
    ap.add_argument("--friend-game", required=True)
    ap.add_argument("--wait", type=int, default=120)
    a = ap.parse_args()
    out = ROOT / "local" / "tests" / a.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    A, B = KIT / "A", KIT / "B"
    R.write_settings(A, "HostTest", a.host_game, "1", "4:3")
    R.write_settings(B, "FriendTest", a.friend_game, "1", "4:3")
    for c in (A, B):
        for f in (c / "logs").glob("*-launcher.txt"):
            f.unlink()
    extra = out / "extra.txt"
    extra.write_text("Bot = random\r\nExitAtFrame = 100000\r\n", encoding="ascii", newline="")
    t0 = time.time()
    stop = threading.Event()
    pids = set()
    threading.Thread(target=R.minimise_loop, args=(stop, pids), daemon=True).start()

    def launch(copy, mode):
        env = dict(os.environ, PS2ONLINE_TEST_EXTRA=str(extra))
        p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                              str(copy / "launcher" / "Launcher.ps1"), "-Test", mode], env=env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pids.add(p.pid)
        return p

    la = launch(A, "host")
    code = None
    while code is None and time.time() - t0 < 120:
        f = R.newest(A / "logs", "*-connection.txt", t0)
        if f:
            m = re.search(r"@code join (\S+)", f.read_text(errors="replace"))
            if m:
                code = m.group(1)
        time.sleep(0.5)
    notes = [f"test {a.name}: mode {a.mode}; host game {a.host_game}; friend game {a.friend_game}"]
    if not code:
        notes.append("FAILED: no join code")
    time.sleep(12)  # the host's game window is up and waiting
    lb = launch(B, "join:" + code if a.mode == "code" else "ip:127.0.0.1")
    t1 = time.time()
    friend_emu_seen = False
    while time.time() - t1 < a.wait:
        procs = subprocess.run(["powershell", "-NoProfile", "-Command",
                                "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like '*kit-test-t\\B\\*' -and $_.Name -eq 'pcsx2-qtx64.exe' } | ForEach-Object { $_.ProcessId }"],
                               capture_output=True, text=True).stdout.split()
        if procs:
            friend_emu_seen = True
        time.sleep(3)
    stop.set()
    for p in (la, lb):
        if p.poll() is None:
            p.kill()
    for pid in R.running("pcsx2-qtx64.exe") + R.running("ps2net-link.exe"):
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    time.sleep(2)
    notes.append(f"friend's emulator process seen: {friend_emu_seen}")
    for tag, copy in (("host", A), ("friend", B)):
        notes.append(f"--- {tag}: what the launcher window said")
        for f in sorted((copy / "logs").glob("*-launcher.txt")):
            for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                if any(w in line for w in ("check", "NOT the same", "Joining", "Hosting", "Game:", "closed", "Connected", "do not have")):
                    notes.append("  " + line[:300])
        g = R.newest(copy / "logs", "*-game.txt", t0)
        notes.append(f"--- {tag}: game log")
        if g:
            shutil.copy2(g, out / f"{tag}_game.txt")
            for line in g.read_text(errors="replace").splitlines():
                if any(w in line for w in ("lobby:", "refused", "Different", "start:", "OUT OF SYNC", "session closed", "left", "error")):
                    notes.append("  " + re.sub(r"\d+\.\d+\.\d+\.\d+", "[ip]", line)[:300])
        else:
            notes.append("  (no game log: the emulator was not started in this session)")
        chk = copy / "emulator" / "patches" / "game-file-check.pnach"
        notes.append(f"  check file: {chk.read_text().strip().splitlines()[-1] if chk.exists() else 'none'}")
    (out / "summary.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
