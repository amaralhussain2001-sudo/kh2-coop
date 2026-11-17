"""Dress rehearsal of the test package on ONE PC: two throw-away copies (local/kit-test-t/A = host, B = friend),
started through their own launchers exactly as the players would (Host a game -> join code -> Join), with the
launcher's test mode pressing the buttons and bots holding the controllers.

  python -I tools/package/rehearse.py <name> --game "<file name in MY-GAMES>" --layout 1 --screen 4:3 --frames 16000
         --script-a p1.txt --script-b p2.txt --snap "f1,f2,..." [--timeout 900]

Results: local/tests/<name>/ (screenshots A_*, B_*, copies of both PCs' log files, summary.txt).
Nothing outside local/kit-test-t and local/tests is written.
"""
import argparse
import ctypes
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time
from ctypes import wintypes

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
KIT = ROOT / "local" / "kit-test-t"
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def exe_of(pid):
    h = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(1024)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            return buf.value
        return ""
    finally:
        kernel32.CloseHandle(h)


def minimise_loop(stop, extra_pids):
    """Keep the rehearsal's windows minimised without taking the keyboard focus."""
    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    kit = str(KIT).lower()

    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in extra_pids or exe_of(pid.value).lower().startswith(kit):
            user32.ShowWindow(hwnd, 7)
        return True

    while not stop.is_set():
        try:
            user32.EnumWindows(proto(cb), 0)
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.25)


def running(name_part):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like '*kit-test-t*' } | "
                          "ForEach-Object { \"$($_.ProcessId)|$($_.ExecutablePath)\" }"],
                         capture_output=True, text=True).stdout
    res = []
    for line in out.splitlines():
        if "|" in line and name_part.lower() in line.lower():
            res.append(int(line.split("|")[0]))
    return res


def write_settings(copy, name, game, layout, screen):
    lines = ["Quality=1", f"Name={name}", f"Layout={layout}", f"Game={game}", f"Screen={screen}", "Fullscreen=False", "Buffer=smooth"]
    (copy / "my-settings.txt").write_bytes(b"\xef\xbb\xbf" + "\r\n".join(lines).encode("utf-8") + b"\r\n")
    ini = copy / "emulator" / "inis" / "PCSX2.ini"
    text = ini.read_text(encoding="utf-8-sig")
    if "[SPU2/Output]" not in text:
        ini.write_text(text.rstrip() + "\n\n[SPU2/Output]\nOutputMuted = true\n", encoding="utf-8")


def newest(folder, pattern, after):
    files = [f for f in folder.glob(pattern) if f.stat().st_mtime >= after - 2]
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--game", required=True)
    ap.add_argument("--layout", default="1")
    ap.add_argument("--screen", default="4:3")
    ap.add_argument("--frames", type=int, default=16000)
    ap.add_argument("--script-a", default="")
    ap.add_argument("--script-b", default="")
    ap.add_argument("--snap", default="")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--snapview", action="store_true", help="snapshots show what each PC shows (own screens)")
    a = ap.parse_args()
    out = ROOT / "local" / "tests" / a.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    A, B = KIT / "A", KIT / "B"
    for c in (A, B):
        if not (c / "MY-GAMES (never share)" / a.game).exists():
            sys.exit(f"{a.game} is missing in {c}")
    write_settings(A, "HostTest", a.game, a.layout, a.screen)
    write_settings(B, "FriendTest", a.game, a.layout, a.screen)
    extras = {}
    for tag, script, seed in (("A", a.script_a, 1007), ("B", a.script_b, 2007)):
        lines = [f"BotSeed = {seed}", f"SnapDir = {out / tag}", "SnapEvery = 0", f"SnapFrames = {a.snap}", f"ExitAtFrame = {a.frames}"]
        if a.snapview:
            lines.append("SnapView = 1")
        if script:
            lines += ["Bot = script", f"Script = {pathlib.Path(script).resolve()}", "BotThen = random"]
        else:
            lines += ["Bot = random"]
        (out / tag).mkdir()
        f = out / f"extra_{tag}.txt"
        f.write_text("\r\n".join(lines) + "\r\n", encoding="ascii", newline="")
        extras[tag] = f
    t0 = time.time()
    stop = threading.Event()
    pids = set()
    if os.environ.get("KH2_TEST_SHOW", "0") != "1":      # KH2_TEST_SHOW=1: the user watches, leave the windows alone
        threading.Thread(target=minimise_loop, args=(stop, pids), daemon=True).start()

    def launch(copy, tag, mode):
        env = dict(os.environ, PS2ONLINE_TEST_EXTRA=str(extras[tag]))
        # The launcher, and the helper and emulator it starts, run on the hidden test desktop (tools/quiet_launch.py),
        # so no window of the rehearsal can take the keyboard focus from the user. KH2_TEST_DESKTOP=0 = old way.
        sys.path.insert(0, str(ROOT / "tools"))
        import quiet_launch
        p = quiet_launch.popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                str(copy / "launcher" / "Launcher.ps1"), "-Test", mode], env=env)
        pids.add(p.pid)
        return p

    notes = []
    la = launch(A, "A", "host")
    code = None
    while code is None and time.time() - t0 < 180:
        f = newest(A / "logs", "*-connection.txt", t0)
        if f:
            m = re.search(r"@code join (\S+)", f.read_text(errors="replace"))
            if m:
                code = m.group(1)
        time.sleep(0.5)
    if not code:
        notes.append("FAILED: the host launcher produced no join code within 180 s")
        lb = None
    else:
        notes.append(f"join code after {time.time() - t0:.0f} s, {len(code)} characters")
        lb = launch(B, "B", "join:" + code)
    # wait until both emulators have started and ended, or the time limit
    seen = set()
    while time.time() - t0 < a.timeout:
        emus = running("pcsx2-qtx64.exe")
        seen |= set(emus)
        if len(seen) >= 2 and not emus:
            break
        time.sleep(2)
    else:
        notes.append("TIME LIMIT reached; processes stopped")
    notes.append(f"emulator processes seen: {len(seen)}, wall {time.time() - t0:.0f} s")
    time.sleep(3)
    stop.set()
    for p in (la, lb):
        if p and p.poll() is None:
            p.kill()
    for pid in running("pcsx2-qtx64.exe") + running("ps2net-link.exe"):
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    # collect
    summary = [f"rehearsal {a.name}: game {a.game}, layout {a.layout}, screen {a.screen}, {a.frames} frames"] + notes
    words = ("lobby:", "start:", "OUT OF SYNC", "session closed", "refused", "Different", "test end", "round trip", "error")
    for tag, copy in (("A", A), ("B", B)):
        for pat in ("*-game.txt", "*-connection.txt"):
            f = newest(copy / "logs", pat, t0)
            if f:
                shutil.copy2(f, out / f"{tag}_{pat[2:]}")
        ses = copy / "logs" / "session.ini"
        if ses.exists():
            shutil.copy2(ses, out / f"{tag}_session.ini")
        chk = copy / "emulator" / "patches" / "game-file-check.pnach"
        g = out / f"{tag}_game.txt"
        summary.append(f"--- {tag}: check file: {chk.read_text().strip().splitlines()[-1] if chk.exists() else 'MISSING'}")
        if g.exists():
            text = g.read_text(errors="replace").splitlines()
            keep = [l for l in text if any(w in l for w in words)]
            summary += keep[:4] + keep[-3:]
            polls = [l for l in text if "polls" in l]
            if polls:
                summary.append(polls[-1])
        else:
            summary.append("no game log")
    shots_a = sorted(p.name for p in (out / "A").glob("*.png"))
    same = 0
    import hashlib
    for n in shots_a:
        other = out / "B" / n.replace("p1_", "p2_")
        if other.exists() and hashlib.sha1((out / "A" / n).read_bytes()).digest() == hashlib.sha1(other.read_bytes()).digest():
            same += 1
    summary.append(f"screenshots: host {len(shots_a)}, friend {len(list((out / 'B').glob('*.png')))}, identical pairs {same}")
    (out / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
