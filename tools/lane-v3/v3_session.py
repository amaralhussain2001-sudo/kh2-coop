"""Lane V3 copy of the sandbox session runner, with the options the own-screen view needs.

Same idea as tools/kh2_session.py (which is shared and not edited): emulator copies under local/<run-dir>/p1..pN,
made from the package's emulator folder, started with a PS2Net session file. Extra here:
  --exe1 / --exe2        emulator exe to put into p1 / p2 before the run (to mix builds)
  --view-file FILE       per-game view settings file (<SERIAL>_<CRC>.view) copied into every copy's patches folder
  --view1 / --view2      session key View for p1 / p2: "" (own part), "off" (whole picture) or a player number
  --snapview1/--snapview2  1 = that copy's snapshots show what the player sees
  --upscale1/--upscale2  GS upscale multiplier of p1 / p2 (per-PC picture quality)
  --aspect               GS aspect ratio setting for every copy (for example "16:9" or "Stretch")

  python -I tools/lane-v3/v3_session.py make [N] [--run-dir run-v3]
  python -I tools/lane-v3/v3_session.py run <name> --iso <file> [...]
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PACKAGE_EMU = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE\emulator")
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


def make(n, run_dir):
    run = ROOT / "local" / run_dir
    if not (PACKAGE_EMU / "pcsx2-qtx64.exe").exists():
        sys.exit(f"package emulator not found at {PACKAGE_EMU}")
    for i in range(1, n + 1):
        d = run / f"p{i}"
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
    rundir = ROOT / "local" / a.run_dir
    out = ROOT / "local" / "tests" / a.name
    out.mkdir(parents=True, exist_ok=True)
    iso = pathlib.Path(a.iso).resolve()
    if not iso.exists():
        sys.exit(f"missing disc image {iso}")
    procs = []
    for k in range(1, a.players + 1):
        d = rundir / f"p{k}"
        exe = d / "pcsx2-qtx64.exe"
        if not d.exists():
            sys.exit(f"missing {d}; run: v3_session.py make {a.players} --run-dir {a.run_dir}")
        new_exe = a.exe1 if k == 1 else a.exe2
        if new_exe:
            shutil.copyfile(new_exe, exe)
        pdir = d / "patches"
        for f in list(pdir.glob("*.pnach")) + list(pdir.glob("*.view")):
            f.unlink()
        if a.patch_dir:
            for f in pathlib.Path(a.patch_dir).glob("*.pnach"):
                (pdir / f.name).write_bytes(f.read_bytes())
        if a.view_file:
            vf = pathlib.Path(a.view_file)
            (pdir / vf.name).write_bytes(vf.read_bytes())
        card = d / "memcards" / "Mcd001.ps2"
        if a.card:
            shutil.copyfile(a.card, card)
        elif a.fresh_card and card.exists():
            card.unlink()
        pini = d / "inis" / "PCSX2.ini"
        text = pini.read_text()
        if "[Framerate]" in text:
            text = text[:text.index("[Framerate]")]
        text = "\n".join(l for l in text.split("\n") if not l.startswith(("EnablePINE", "PINESlot")))
        pine_port = a.pine if k == 1 else a.pine2
        if pine_port:
            text = text.replace("EnableDiscordPresence = false",
                                f"EnableDiscordPresence = false\nEnablePINE = true\nPINESlot = {pine_port}")
        extra = ""
        gs = []
        up = a.upscale1 if k == 1 else a.upscale2
        if up:
            gs += [f"upscale_multiplier = {up}", "ExtendedUpscalingMultipliers = true"]
        if a.aspect:
            gs.append(f"AspectRatio = {a.aspect}")
        if a.shot_internal:
            gs.append("ScreenshotSize = 1")
        if a.shot_raw:
            gs.append("ScreenshotSize = 2")
        if gs:
            extra += "\n[EmuCore/GS]\n" + "\n".join(gs) + "\n"
        pini.write_text(text.rstrip() + f"\n\n[Framerate]\nNominalScalar = {a.speed}\n" + extra)
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
            f"DumpFrames = {a.dump}",
            f"Peek = {a.peek}",
            f"Screen = {a.screen}",
        ]
        extra = a.extra1 if k == 1 else a.extra2
        if extra:
            lines += [x.strip() for x in extra.split("|") if x.strip()]   # test only: raw session lines ("Key = value|Key = value")
        view = a.view1 if k == 1 else a.view2
        if view:
            lines.append(f"View = {view}")
        if (a.snapview1 if k == 1 else a.snapview2):
            lines.append("SnapView = 1")
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
            # (tools/quiet_launch.py). KH2_TEST_DESKTOP=0 switches this off.
            sys.path.insert(0, str(ROOT / "tools"))
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
               f"wall {time.time() - t0:.0f} s" + (" (TIMED OUT, emulator killed)" if timed_out else "")]
    words = ("start:", "OUT OF SYNC", "test end", "session closed", "refused", "error", "warning", "delay",
             "dropped", "lobby:", "view:", "Different")
    for k in range(1, a.players + 1):
        log = out / f"p{k}.log"
        try:
            text = log.read_text(errors="replace") if log.exists() else ""
        except OSError as e:
            text = f"(cannot read log: {e})"
        keep = [l for l in text.splitlines() if any(w in l for w in words)]
        summary.append(f"--- p{k} (exit {procs[k - 1].returncode})")
        summary += keep[:4] + keep[4:][-(a.tail):]
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("n", type=int, nargs="?", default=2)
    m.add_argument("--run-dir", default="run-v3")
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--iso", required=True)
    r.add_argument("--players", type=int, default=2)
    r.add_argument("--frames", type=int, default=3600)
    r.add_argument("--speed", type=float, default=2.0)
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
    r.add_argument("--port", type=int, default=30150)
    r.add_argument("--timeout", type=int, default=900)
    r.add_argument("--tail", type=int, default=8)
    r.add_argument("--pine", type=int, default=0)
    r.add_argument("--pine2", type=int, default=0)
    r.add_argument("--dump", default="", help="frames at which every copy writes its main memory (lane V3 build only)")
    r.add_argument("--run-dir", default="run-v3")
    r.add_argument("--show", action="store_true")
    r.add_argument("--exe1", default="")
    r.add_argument("--exe2", default="")
    r.add_argument("--view-file", default="")
    r.add_argument("--view1", default="")
    r.add_argument("--view2", default="")
    r.add_argument("--snapview1", type=int, default=0)
    r.add_argument("--snapview2", type=int, default=0)
    r.add_argument("--extra1", default="", help="raw session lines for p1, separated by | (test only, e.g. TestPoke = 6000:000D1000:5A)")
    r.add_argument("--extra2", default="", help="raw session lines for p2, separated by |")
    r.add_argument("--upscale1", type=int, default=0)
    r.add_argument("--upscale2", type=int, default=0)
    r.add_argument("--aspect", default="")
    r.add_argument("--shot-internal", action="store_true", help="screenshots at internal resolution")
    r.add_argument("--shot-raw", action="store_true", help="screenshots at internal resolution, no aspect correction")
    a = ap.parse_args()
    # TEST ONLY (part 142): the whole regression at different picture quality: PIC_EXE (both copies), PIC_VIEW (the .view file),
    # PIC_UP1 / PIC_UP2 (each copy's upscale) override the options when set.
    if getattr(a, "iso", None) is not None:
        if os.environ.get("PIC_EXE"):
            a.exe1 = a.exe2 = os.environ["PIC_EXE"]
        if os.environ.get("PIC_VIEW"):
            a.view_file = os.environ["PIC_VIEW"]
        if os.environ.get("PIC_UP1"):
            a.upscale1 = int(os.environ["PIC_UP1"])
        if os.environ.get("PIC_UP2"):
            a.upscale2 = int(os.environ["PIC_UP2"])
    if a.cmd == "make":
        make(a.n, a.run_dir)
    else:
        run(a)


if __name__ == "__main__":
    main()
