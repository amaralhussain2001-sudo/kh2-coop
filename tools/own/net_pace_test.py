"""Frame pacing over a simulated internet link, on ONE PC (user report 2026-11-17: "the fps is not stable").

Two throw-away copies of a package's emulator folder (A = host, B = friend) under local/run-net/, the two-player
disc, both controllers held by random bots, and the emulator's own network impairment (each copy delays every
packet it sends by ImpairDelay + 0..ImpairJitter ms). Nothing outside local/run-net and local/tests is written.

  python -I tools/own/net_pace_test.py <name> [--emu DIR] [--exe FILE] [--frames 6000] [--idelay 35] [--ijitter 60]
         [--buffer smooth] [--screen 16:9] [--port 32750]

Prints, per PC: frames, waits, time waited, the time the session lost against a perfect 59.94 Hz, and the
"repaid" part (waited - lost: time the PC waited and then won back by running frames faster than 60 Hz).
"""
import argparse
import os
import pathlib
import re
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import quiet_launch  # noqa: E402

DEFAULT_EMU = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2\emulator")  # read only
DISC = ROOT / "local" / "iso" / "kh2-coop-v5.iso"
# the b24 exe as shipped (the Desktop b24 folder may hold the build 25 exe once the user applied the update)
OLD_EXE = ROOT / "emulator-src" / "builds" / "view12" / "pcsx2-qtx64.exe"
RUN = ROOT / "local" / "run-net"
SKIP = {"logs", "snaps", "sstates", "videos"}
FPS = 59.94


def make_copy(src, dst, exe):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=lambda d, names: [n for n in names if pathlib.Path(d) == src and n in SKIP])
    for sub in ("logs", "snaps"):
        (dst / sub).mkdir(exist_ok=True)
    shutil.copy2(exe or OLD_EXE, dst / "pcsx2-qtx64.exe")


def parse(log):
    text = log.read_text(errors="replace") if log.exists() else ""
    start = re.search(r"^(\d+) start: ", text, re.M)
    stats = re.findall(r"^(\d+) stats: frame (\d+), waits (\d+), wait total (\d+) ms, longest (\d+) ms.*?(in sync|OUT OF SYNC[^\n]*)$",
                       text, re.M)
    closed = re.search(r"^(\d+) session closed at frame (\d+)", text, re.M)
    delay = re.search(r"input delay (\d+) frames|delay (\d+) frames", text)
    if not start or not stats:
        return None
    t0 = int(start.group(1))
    last = stats[-1]
    t1, frames = int(last[0]), int(last[1])
    waits, waited, longest = int(last[2]), int(last[3]), int(last[4])
    elapsed = (t1 - t0) / 1000.0
    lost = elapsed - frames / FPS
    windows = []
    prev = None
    for s in stats:
        cur = (int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        if prev and cur[1] > prev[1]:
            windows.append((cur[1] - prev[1], cur[2] - prev[2], cur[3] - prev[3]))
        prev = cur
    sync = "OUT OF SYNC" if "OUT OF SYNC" in text else "in sync"
    d = delay.group(1) or delay.group(2) if delay else "?"
    return dict(frames=frames, waits=waits, waited=waited / 1000.0, longest=longest, elapsed=elapsed, lost=lost,
                windows=windows, sync=sync, delay=d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--emu", default=str(DEFAULT_EMU))
    ap.add_argument("--exe", default="")
    ap.add_argument("--exe2", default=None, help="the friend copy's exe when it differs (mixed versions); default = --exe")
    ap.add_argument("--frames", type=int, default=6000)
    ap.add_argument("--idelay", type=int, default=35)
    ap.add_argument("--ijitter", type=int, default=60)
    ap.add_argument("--buffer", default="smooth")
    ap.add_argument("--screen", default="16:9")
    ap.add_argument("--port", type=int, default=32750)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--reuse", action="store_true", help="keep the copies of the last run (same exe)")
    ap.add_argument("--card1", default="", help="memory card file for the host copy (default: the package's)")
    ap.add_argument("--card2", default="", help="memory card file for the friend copy (default: the package's)")
    ap.add_argument("--loss", type=int, default=0, help="ImpairLoss percent on both copies")
    ap.add_argument("--delay", type=int, default=0, help="input delay in frames (0 = the host chooses, as in play)")
    ap.add_argument("--speed2", type=float, default=1.0,
                    help="friend copy's target speed (0.99 = a PC that cannot quite hold 60 Hz); not part of the sync check")
    a = ap.parse_args()
    src = pathlib.Path(a.emu)
    out = ROOT / "local" / "tests" / a.name
    out.mkdir(parents=True, exist_ok=True)
    procs = []
    for k, role in ((1, "host"), (2, "client")):
        d = RUN / ("A" if k == 1 else "B")
        if not (a.reuse and d.exists()):
            make_copy(src, d, a.exe if (k == 1 or a.exe2 is None) else a.exe2)
        card = a.card1 if k == 1 else a.card2
        if card:
            for old in (d / "memcards").glob("*"):
                old.unlink()
            shutil.copyfile(card, d / "memcards" / "Mcd001.ps2")
        ini_emu = d / "inis" / "PCSX2.ini"
        text = ini_emu.read_text(encoding="utf-8-sig")
        if "[Framerate]" in text:
            text = text[:text.index("[Framerate]")]
        speed = a.speed2 if k == 2 else 1.0
        ini_emu.write_text(text.rstrip() + f"\n\n[Framerate]\nNominalScalar = {speed}\n", encoding="utf-8")
        log = out / f"p{k}.log"
        if log.exists():
            log.unlink()
        lines = [f"Role = {role}", "Host = 127.0.0.1", f"Port = {a.port}", "Players = 2", f"Name = Bot{k}",
                 "Slots = 0,1", f"Screen = {a.screen}", f"Buffer = {a.buffer}", "Bot = random", f"BotSeed = {k * 1000 + 7}",
                 f"LogFile = {log}", f"ExitAtFrame = {a.frames}", f"Delay = {a.delay}", f"ImpairDelay = {a.idelay}", f"ImpairJitter = {a.ijitter}", f"ImpairLoss = {a.loss}"]
        ini = out / f"session_p{k}.ini"
        ini.write_text("\n".join(lines) + "\n")
        env = dict(os.environ, PS2NET_CONFIG=str(ini))
        console = open(out / f"p{k}_console.txt", "w")
        procs.append(quiet_launch.popen([str(d / "pcsx2-qtx64.exe"), "-batch", "-fastboot", "--", str(DISC)], env=env,
                                        cwd=str(d), stdout=console))
        time.sleep(1.0)
    t0 = time.time()
    while any(p.poll() is None for p in procs) and time.time() - t0 < a.timeout:
        time.sleep(2)
    for p in procs:
        if p.poll() is None:
            p.kill()
    rows = [f"test {a.name}: exe {a.exe or 'view12 (b24)'} / friend {(a.exe or 'view12 (b24)') if a.exe2 is None else (a.exe2 or 'view12 (b24)')}, impair {a.idelay}+0..{a.ijitter} ms each way, buffer {a.buffer}, friend speed {a.speed2}, "
            f"{a.frames} frames, wall {time.time() - t0:.0f} s"]
    for k in (1, 2):
        r = parse(out / f"p{k}.log")
        if not r:
            rows.append(f"p{k}: no result")
            continue
        rows.append(f"p{k} ({'host' if k == 1 else 'friend'}): delay {r['delay']}, frames {r['frames']} in {r['elapsed']:.1f} s "
                    f"({r['frames'] / r['elapsed']:.2f}/s), waits {r['waits']}, waited {r['waited']:.1f} s, longest {r['longest']} ms, "
                    f"lost {r['lost']:.1f} s, repaid {r['waited'] - r['lost']:.1f} s, {r['sync']}")
        rows.append("    per 10 s (frames/waits/ms): " + " ".join(f"{f}/{w}/{m}" for f, w, m in r["windows"]))
    (out / "summary.txt").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
