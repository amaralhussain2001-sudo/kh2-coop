"""Build the two-player disc v3 = build_disc_v2.py + MAIL DELIVERY FOR TWO (tools/lane-s1/make_mail.py: a second
skateboard in the two Mail Delivery groups of tt06, and mission scripts that put the twin on it).
The rest of this text is build_disc_v2.py's.

Build the two-player disc WITH the boss HP change (merged build 4 and later).

  python -I tools/merge/build_disc_v3.py <outIsoName> [--no-mail] [--boss-percent 75] [--capped] [--overlay DIR ...]
                                         [--no-twin] [--rooms a,b] [--jump "WORLD LOCALSET"] [--party NO_FRIEND]

  <outIsoName>    file name inside local/iso, for example kh2-coop-v2.iso
  --boss-percent  THE ONE NUMBER (user decision 7: 75). Single bosses can have their own number in
                  tools/lane-b75/data/boss_entries.csv (user decision 2026-11-10: Pete at Olympus, entry 26, = 40).
  --capped        use the gauge cap instead of the gauge patch (NOT the user's choice; kept for tests)
  --jump          TEST DISCS ONLY: New Game jumps straight to the room that owns program LOCALSET of WORLD
                  (lane B's method, same recipe as tools/lane-b75/build_disc_b75.py)

Steps, all deterministic (same inputs give the same bytes):
  1. the twins: lane F's tool exactly as tools/merge/build_disc_m.py runs it for kh2-coop-v1.iso
     (local/build/lane-f/LaneF.dll twin-all, twin record BEFORE the placeholder, also 54);
  2. boss HP: tools/lane-b75/scale_boss_hp.py writes the changed 00battle.bin into the same build folder.
     Default is --gauge-patch (no cap): the disc must be played with a game patch that contains lane B75's gauge
     lines (patches/merged-v4 or later);
  3. the shared tool Kh2Tool inject writes everything into a COPY of the English text build 3 candidate.
The base image, the original disc and the other lanes' files are only read.
Work files and reports: local/variants/v2-<name>/.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
LANEF = ROOT / "local" / "build" / "lane-f" / "LaneF.dll"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
BUILD3 = ROOT / "local" / "iso" / "English text build3 (candidate).iso"
EXTRACT = ROOT / "local" / "extract" / "kh2"
ARD = EXTRACT / "ard"
MAP = EXTRACT / "map" / "jp"
SCALE = ROOT / "tools" / "lane-b75" / "scale_boss_hp.py"
MAIL = ROOT / "tools" / "lane-s1" / "make_mail.py"

MOD_YML = """title: jump start (tests only)
game: kh2
assets:
  - name: ard/tt01.ard
    method: binarc
    source:
      - name: evt
        type: AreaDataScript
        method: areadatascript
        source:
          - name: tt01_evt.txt
"""


def run(cmd, env):
    out = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if out.stdout.strip():
        print(out.stdout.strip())
    if out.returncode:
        sys.exit(out.stderr or f"command failed: {cmd}")
    return out.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--boss-percent", type=int, default=75)
    ap.add_argument("--capped", action="store_true")
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--no-twin", action="store_true")
    ap.add_argument("--rooms", default="")
    ap.add_argument("--also", default="54")
    ap.add_argument("--jump", default="")
    ap.add_argument("--party", default="NO_FRIEND")
    ap.add_argument("--base", default=str(BUILD3))
    ap.add_argument("--no-mail", action="store_true")
    a = ap.parse_args()

    stem = pathlib.Path(a.name).stem
    var = ROOT / "local" / "variants" / ("v3-" + stem)
    if var.exists():
        shutil.rmtree(var)
    var.mkdir(parents=True)
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_CLI_HOME=str(ROOT / "local" / "dotnet-home"))
    overlays = [str(pathlib.Path(o).resolve()) for o in a.overlay]
    mail_serials = None
    if not a.no_mail and not a.no_twin:
        out = run([sys.executable, "-I", str(MAIL), "ard", str(var / "mail" / "ard")], env)
        print(out.strip())
        mail_serials = [int(x) for x in re.findall(r"serial (\d+);", out)]
        assert len(mail_serials) == 2, out
        overlays.append(str(var / "mail" / "ard"))
    if a.jump:
        mod = var / "mod"
        mod.mkdir()
        (mod / "mod.yml").write_text(MOD_YML)
        world, localset = a.jump.split()
        lines = ["Program 0x34"]
        if a.party != "-":
            lines.append(f"Party {a.party}")
        lines += ["Bgm Default Default", "AreaSettings 0 -1",
                  f" SetJump Type 2 World {world} Area 0 Entrance 0 LocalSet {localset} FadeType 16386",
                  " SetPartyMenu 0", ""]
        (mod / "tt01_evt.txt").write_text("\n".join(lines))
        run([str(DOTNET), str(KH2TOOL), "patch", str(EXTRACT), str(mod), str(var / "jump")], env)
        overlays.append(str(var / "jump" / "ard"))

    built = var / "built"
    if a.no_twin:
        (built / "ard").mkdir(parents=True)
        for o in overlays:
            for f in sorted(pathlib.Path(o).glob("*.ard")):
                shutil.copyfile(f, built / "ard" / f.name)
        print("no twins; overlay files:", sorted(p.name for p in (built / "ard").iterdir()))
    else:
        rooms = a.rooms
        if rooms and a.jump and "tt01" not in rooms.split(","):
            rooms += ",tt01"
        cmd = [str(DOTNET), str(LANEF), "twin-all", str(ARD), ";".join(overlays) or "-", str(MAP),
               str(built), str(var / "report.csv"), "before", rooms or "-", a.also or "-"]
        (var / "twin-all.txt").write_text(run(cmd, env))
        for o in overlays:      # with --rooms the placement tool only writes those rooms; the jump recipe must go in
            for f in sorted(pathlib.Path(o).glob("*.ard")):
                if not (built / "ard" / f.name).exists():
                    (built / "ard").mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, built / "ard" / f.name)

    if mail_serials:
        print(run([sys.executable, "-I", str(MAIL), "msn", str(built), str(var / "report.csv"),
                   str(mail_serials[0]), str(mail_serials[1])], env).strip())

    if a.boss_percent != 0:
        cmd = [sys.executable, "-I", str(SCALE), str(EXTRACT / "00battle.bin"), str(built / "00battle.bin"),
               "--percent", str(a.boss_percent), "--report", str(var / "boss-hp-report.txt")]
        if not a.capped:
            cmd.append("--gauge-patch")
        run(cmd, env)
    else:
        print("boss HP: battle file not touched")

    iso = ROOT / "local" / "iso" / a.name
    run([str(DOTNET), str(KH2TOOL), "inject", a.base, str(iso), str(built), str(var / "inject-report.txt")], env)
    print("disc:", iso)


if __name__ == "__main__":
    main()
