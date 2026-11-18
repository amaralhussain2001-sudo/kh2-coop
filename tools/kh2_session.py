"""Sandbox emulator sessions for the KH2 two-player project.

Nothing here writes to Desktop\\PS2-ONLINE: the emulator is COPIED from it into local/run/p1..pN and only the
copies are started. The disc image is opened by the emulator read-only.

  python -I tools/kh2_session.py make [N]
  python -I tools/kh2_session.py run <name> --iso <file> [--players 1] [--frames 3600] [--speed 1]
         [--snap-every 0] [--snap "f1,f2"] [--script p1.txt] [--script2 p2.txt] [--bot none] [--then idle]
         [--slots 0,1] [--peek hex,hex] [--screen 4:3] [--patch-dir DIR] [--card FILE] [--timeout 900]

Results go to local/tests/<name>/ (session files, PS2Net logs, screenshots, summary.txt).
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE_EMU = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE\emulator")
RUN = ROOT / "local" / "run"
# user data of the package that must not travel into the sandbox copies
SKIP_DIRS = {"cache", "logs", "memcards", "sstates", "snaps", "inis", "videos", "covers", "textures",
             "gamesettings", "cheats", "patches", "inputprofiles"}

INI = """[UI]
SettingsVersion = 1
SetupWizardIncomplete = false
ConfirmShutdown = false
StartPaused = false
PauseOnFocusLoss = false
StartFullscreen = false
HideMouseCursor = false
RenderToSeparateWindow = false

[Folders]
Bios = bios
MemoryCards = memcards
Snapshots = snaps
Savestates = sstates
Logs = logs

[Filenames]
BIOS = SCPH-90001_BIOS_V18_USA_230.ROM0

[EmuCore]
EnableFastBoot = true
EnableDiscordPresence = false

[SPU2/Output]
OutputMuted = true

[MemoryCards]
Slot1_Enable = true
Slot1_Filename = Mcd001.ps2
Slot2_Enable = false

[InputSources]
Keyboard = true
SDL = false

[AutoUpdater]
CheckAtStartup = false

[Pad1]
Type = DualShock2
"""


def make(n):
    global RUN
    if "--run-dir" in sys.argv:
        RUN = ROOT / "local" / sys.argv[sys.argv.index("--run-dir") + 1]
    if not (PACKAGE_EMU / "pcsx2-qtx64.exe").exists():
        sys.exit(f"package emulator not found at {PACKAGE_EMU}")
    for i in range(1, n + 1):
        d = RUN / f"p{i}"
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for item in PACKAGE_EMU.iterdir():
            if item.is_dir():
                if item.name.lower() in SKIP_DIRS:
                    continue
                shutil.copytree(item, d / item.name)
            else:
                shutil.copy2(item, d / item.name)
        for sub in ("inis", "memcards", "snaps", "sstates", "logs", "patches", "cheats"):
            (d / sub).mkdir(exist_ok=True)
        (d / "portable.txt").write_text("")
        (d / "inis" / "PCSX2.ini").write_text(INI)
        print("made", d)


def keep_minimized(pid, seconds=25.0):
    """Minimise the test emulator's windows without taking the keyboard focus (so tests do not pop up over the
    user's work). Only the window state changes; the emulated game is not affected."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    done = set()

    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and user32.IsWindowVisible(hwnd) and hwnd not in done and not user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 7)  # SW_SHOWMINNOACTIVE
            done.add(hwnd)
        return True

    end = time.time() + seconds
    while time.time() < end:
        try:
            user32.EnumWindows(proto(cb), 0)
        except Exception:  # noqa: BLE001
            return
        time.sleep(0.1)


def run(a):
    global RUN
    RUN = ROOT / "local" / a.run_dir
    out = ROOT / "local" / "tests" / a.name
    out.mkdir(parents=True, exist_ok=True)
    iso = pathlib.Path(a.iso).resolve()
    if not iso.exists():
        sys.exit(f"missing disc image {iso}")
    procs = []
    for k in range(1, a.players + 1):
        d = RUN / f"p{k}"
        exe = d / "pcsx2-qtx64.exe"
        if not exe.exists():
            sys.exit(f"missing {exe}; run: kh2_session.py make {a.players}")
        pdir = d / "patches"
        for f in pdir.glob("*.pnach"):
            f.unlink()
        if a.patch_dir:
            for f in pathlib.Path(a.patch_dir).glob("*.pnach"):
                (pdir / f.name).write_bytes(f.read_bytes())
        card = d / "memcards" / "Mcd001.ps2"
        if a.card:
            shutil.copyfile(a.card, card)
        elif a.fresh_card and card.exists():
            card.unlink()
        pini = d / "inis" / "PCSX2.ini"
        text = pini.read_text()
        if "[Framerate]" in text:
            text = text[:text.index("[Framerate]")]
        # PINE (memory read interface) only on player 1 and only when asked; it is a read-only debugging aid.
        text = "\n".join(l for l in text.split("\n") if not l.startswith(("EnablePINE", "PINESlot")))
        if a.pine and k == 1:
            text = text.replace("EnableDiscordPresence = false",
                                f"EnableDiscordPresence = false\nEnablePINE = true\nPINESlot = {a.pine}")
        extra = ""
        if a.ee_rate:
            # emulated CPU speed step: 1 = 130 %, 2 = 180 %, 3 = 300 % (0 = real PS2). Must be equal on all copies.
            extra = f"\n[EmuCore/Speedhacks]\nEECycleRate = {a.ee_rate}\n"
        up = os.environ.get("PIC_UP1" if k == 1 else "PIC_UP2")   # TEST ONLY (part 142): picture quality per copy
        if up:
            extra += f"\n[EmuCore/GS]\nupscale_multiplier = {int(up)}\nExtendedUpscalingMultipliers = true\n"
        pini.write_text(text.rstrip() + f"\n\n[Framerate]\nNominalScalar = {a.speed}\n" + extra)
        if os.environ.get("PIC_EXE"):                                     # TEST ONLY (part 142): another emulator build
            shutil.copy2(os.environ["PIC_EXE"], d / "pcsx2-qtx64.exe")
        for f in pdir.glob("*.view"):
            f.unlink()
        if os.environ.get("PIC_VIEW"):                                    # TEST ONLY (part 142): the game's .view file
            shutil.copy2(os.environ["PIC_VIEW"], pdir / pathlib.Path(os.environ["PIC_VIEW"]).name)
        lines = [
            f"Role = {'host' if k == 1 else 'client'}",
            "Host = 127.0.0.1",
            f"Port = {a.port}",
            f"Players = {a.players}",
            f"Name = Bot{k}",
            f"Delay = {a.delay}",
            f"Slots = {a.slots}",
            f"BotSeed = {k * 1000 + 7}",
            f"LogFile = {out / f'p{k}.log'}",
            f"SnapDir = {out}",
            f"SnapEvery = {a.snap_every}",
            f"SnapFrames = {a.snap}",
            f"ExitAtFrame = {a.frames}",
            f"Peek = {a.peek}",
            f"Screen = {a.screen}",
        ]
        script = a.script if k == 1 else a.script2
        if script:
            lines += ["Bot = script", f"Script = {pathlib.Path(script).resolve()}", f"BotThen = {a.then}"]
        else:
            lines.append(f"Bot = {a.bot}")
        ini = out / f"session_p{k}.ini"
        ini.write_text("\n".join(lines) + "\n")
        log = out / f"p{k}.log"
        if log.exists():
            log.unlink()
        env = dict(os.environ, PS2NET_CONFIG=str(ini))
        console = open(out / f"p{k}_console.txt", "w")
        if a.show:
            procs.append(subprocess.Popen([str(exe), "-batch", "-fastboot", "--", str(iso)], env=env,
                                          cwd=str(d), stdout=console, stderr=subprocess.STDOUT))
        else:
            # Tests must not disturb the user: the emulator starts on a separate hidden Windows desktop
            # (tools/quiet_launch.py), so its window can never take the keyboard focus. KH2_TEST_DESKTOP=0 switches
            # this off; then the old way (minimise the window right after it appears) is used.
            sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
            import quiet_launch
            procs.append(quiet_launch.popen([str(exe), "-batch", "-fastboot", "--", str(iso)], env=env,
                                            cwd=str(d), stdout=console))
            if quiet_launch.SHOW:
                threading.Thread(target=quiet_launch.place, args=(procs[-1].pid, k - 1), daemon=True).start()
            elif not quiet_launch.ENABLED:
                threading.Thread(target=keep_minimized, args=(procs[-1].pid,), daemon=True).start()
        time.sleep(1.0)
    t0 = time.time()
    while any(p.poll() is None for p in procs) and time.time() - t0 < a.timeout:
        time.sleep(2)
    timed_out = any(p.poll() is None for p in procs)
    for p in procs:
        if p.poll() is None:
            p.kill()
    summary = [f"test {a.name}: disc {iso.name}, {a.players} player(s), {a.frames} frames, speed {a.speed}, "
               f"script {a.script or '-'} / {a.script2 or '-'}, wall {time.time() - t0:.0f} s"
               + (" (TIMED OUT, emulator killed)" if timed_out else "")]
    words = ("start:", "OUT OF SYNC", "test end", "session closed", "refused", "error", "warning", "delay",
             "dropped", "lobby:", "polls", "peek")
    for k in range(1, a.players + 1):
        log = out / f"p{k}.log"
        try:
            text = log.read_text(errors="replace") if log.exists() else ""
        except OSError as e:
            text = f"(cannot read log: {e})"
        keep = [l for l in text.splitlines() if any(w in l for w in words)]
        summary.append(f"--- p{k} (exit {procs[k - 1].returncode})")
        summary += keep[:3] + keep[-(a.tail):]
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("n", type=int, nargs="?", default=2)
    m.add_argument("--run-dir", default="run", help="folder under local/ for the emulator copies (one per work lane)")
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--iso", required=True)
    r.add_argument("--players", type=int, default=1)
    r.add_argument("--frames", type=int, default=3600)
    r.add_argument("--speed", type=float, default=1.0)
    r.add_argument("--snap-every", type=int, default=0)
    r.add_argument("--snap", default="")
    r.add_argument("--script", default="")
    r.add_argument("--script2", default="")
    r.add_argument("--bot", default="none")
    r.add_argument("--then", default="idle")
    r.add_argument("--slots", default="0,1")
    r.add_argument("--delay", type=int, default=0)
    r.add_argument("--peek", default="")
    r.add_argument("--screen", default="")
    r.add_argument("--patch-dir", default="")
    r.add_argument("--card", default="")
    r.add_argument("--fresh-card", action="store_true")
    r.add_argument("--port", type=int, default=28350)
    r.add_argument("--timeout", type=int, default=900)
    r.add_argument("--tail", type=int, default=10)
    r.add_argument("--pine", type=int, default=0, help="enable PINE on player 1 at this TCP port (e.g. 28011)")
    r.add_argument("--run-dir", default="run", help="folder under local/ with the emulator copies to use")
    r.add_argument("--show", action="store_true", help="leave the emulator windows on screen (default: minimised)")
    r.add_argument("--ee-rate", type=int, default=0, help="emulated CPU speed step 0..3 (0 = real PS2, 3 = 300 %%)")
    a = ap.parse_args()
    if a.cmd == "make":
        make(a.n)
    else:
        run(a)


if __name__ == "__main__":
    main()
