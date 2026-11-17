"""Lane B75: build a test disc (jump start, twin beside every player placement) with or without the boss HP change.

  python -I tools/lane-b75/build_disc_b75.py <name> [--boss-percent 75] [--jump "WORLD LOCALSET" | --jump1 "WORLD AREA ENTRANCE"]
         [--party NO_FRIEND|DEFAULT|W_FRIEND|-] [--rooms a,b] [--no-twin] [--list FILE] [--gauge-patch]

  <name>          result: local/iso/test-b75-<name>.iso, work files in local/variants/b75-<name>/
  --boss-percent  THE ONE NUMBER. 75 = bosses get 75 % more HP. 0 = control disc: the battle file is not touched.
  --gauge-patch   no gauge cap (see scale_boss_hp.py): only for discs played with the HP gauge lines in the game patch
  --jump          New Game jumps to the room that owns program LOCALSET of WORLD (lane B's test method)
  --rooms         add twins only in these rooms (faster builds); default: every room

Steps, all deterministic: (1) optional jump recipe with the shared Kh2Tool `patch`; (2) lane J's placement tool
(local/build/lane-j/LaneJ.dll, used as it is, with its override file) adds the twins; (3) tools/lane-b75/scale_boss_hp.py
writes the changed 00battle.bin into the same build folder; (4) the shared Kh2Tool `inject` writes everything into a
COPY of the English build 3 candidate. Nothing else is modified.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
LANEJ = ROOT / "local" / "build" / "lane-j" / "LaneJ.dll"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
BASE = ROOT / "local" / "iso" / "English text build3 (candidate).iso"
EXTRACT = ROOT / "local" / "extract" / "kh2"
ARD = EXTRACT / "ard"
MAP = EXTRACT / "map" / "jp"
OVERRIDES = ROOT / "tools" / "lane-j" / "data" / "overrides.csv"
SCALE = ROOT / "tools" / "lane-b75" / "scale_boss_hp.py"

MOD_YML = """title: lane B75 jump (tests only)
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
    ap.add_argument("--list", default="")
    ap.add_argument("--gauge-patch", action="store_true",
                    help="no gauge cap: the disc will be played with a game patch that contains the HP gauge lines")
    ap.add_argument("--jump", default="")
    ap.add_argument("--jump1", default="")
    ap.add_argument("--party", default="NO_FRIEND")
    ap.add_argument("--rooms", default="")
    ap.add_argument("--no-twin", action="store_true")
    ap.add_argument("--no-disc", action="store_true")
    a = ap.parse_args()

    var = ROOT / "local" / "variants" / f"b75-{a.name}"
    if var.exists():
        shutil.rmtree(var)
    var.mkdir(parents=True)
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_CLI_HOME=str(ROOT / "local" / "dotnet-home"))
    overlays = []
    if a.jump or a.jump1:
        mod = var / "mod"
        mod.mkdir()
        (mod / "mod.yml").write_text(MOD_YML)
        if a.jump:
            world, localset = a.jump.split()
            jump = f" SetJump Type 2 World {world} Area 0 Entrance 0 LocalSet {localset} FadeType 16386"
        else:
            world, area, entrance = a.jump1.split()
            jump = f" SetJump Type 1 World {world} Area {area} Entrance {entrance} LocalSet 0 FadeType 16386"
        lines = ["Program 0x34"]
        if a.party != "-":
            lines.append(f"Party {a.party}")
        lines += ["Bgm Default Default", "AreaSettings 0 -1", jump, " SetPartyMenu 0", ""]
        (mod / "tt01_evt.txt").write_text("\n".join(lines))
        run([str(DOTNET), str(KH2TOOL), "patch", str(EXTRACT), str(mod), str(var / "jump")], env)
        overlays.append(str(var / "jump" / "ard"))

    built = var / "built"
    if a.no_twin:
        (built / "ard").mkdir(parents=True)
        for o in overlays:
            for f in pathlib.Path(o).glob("*.ard"):
                shutil.copyfile(f, built / "ard" / f.name)
    else:
        rooms = a.rooms
        if rooms and (a.jump or a.jump1) and "tt01" not in rooms.split(","):
            rooms += ",tt01"
        cmd = [str(DOTNET), str(LANEJ), "twin-all", str(ARD), ";".join(overlays) or "-", str(MAP), str(built),
               str(var / "report.csv"), "before", rooms or "-", "54", str(OVERRIDES)]
        (var / "twin-all.txt").write_text(run(cmd, env))
        # with --rooms the placement tool only writes those rooms; the jump recipe must still go in
        for o in overlays:
            for f in pathlib.Path(o).glob("*.ard"):
                if not (built / "ard" / f.name).exists():
                    (built / "ard").mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, built / "ard" / f.name)
    if a.boss_percent != 0:
        cmd = [sys.executable, "-I", str(SCALE), str(EXTRACT / "00battle.bin"), str(built / "00battle.bin"),
               "--percent", str(a.boss_percent), "--report", str(var / "boss-hp-report.txt")]
        if a.list:
            cmd += ["--list", a.list]
        if a.gauge_patch:
            cmd += ["--gauge-patch"]
        run(cmd, env)
    else:
        print("boss HP: control disc, battle file not touched")
    if a.no_disc:
        return
    iso = ROOT / "local" / "iso" / f"test-b75-{a.name}.iso"
    run([str(DOTNET), str(KH2TOOL), "inject", str(BASE), str(iso), str(built), str(var / "inject-report.txt")], env)
    print("disc:", iso)


if __name__ == "__main__":
    main()
