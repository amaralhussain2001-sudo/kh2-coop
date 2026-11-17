"""Lane S1: build a test disc from the English build 3 candidate with a "jump" start and a twin beside every
player placement. Copy of lane J's build_disc.py (which is a copy of lane F's) with lane S1 names and base.

  python -I tools/lane-s1/build_disc.py <name> [--jump "WORLD LOCALSET" | --jump1 "WORLD AREA ENTRANCE"]
         [--party NO_FRIEND|DEFAULT|W_FRIEND|-] [--overlay DIR ...] [--order before|after] [--rooms a,b]
         [--also 54|-] [--no-twin] [--extra DIR] [--override FILE] [--no-disc]

  <name>     result: local/iso/test-s1-<name>.iso, work files (the recipe) in local/variants/s1-<name>/
  --jump     New Game jumps with a "Type 2" jump to the room that owns program LOCALSET of WORLD (lane B's method)
  --jump1    New Game jumps with a "Type 1" jump (programs from the fresh save: free roam) to WORLD AREA ENTRANCE
  --overlay  folder(s) with *.ard files that replace the stock ones first (twins are still added to them)
  --extra    folder(s) with *.ard files that replace the result LAST (hand-made test rooms; no twin is added)
  --no-twin  do not add twins (control disc)
The original disc, the English copies and the other lanes' tools are only read / run.
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
BUILD3 = ROOT / "local" / "iso" / "English text build3 (candidate).iso"
OVERRIDES = ROOT / "tools" / "lane-j" / "data" / "overrides.csv"
EXTRACT = ROOT / "local" / "extract" / "kh2"
ARD = EXTRACT / "ard"
MAP = EXTRACT / "map" / "jp"

MOD_YML = """title: lane S1 jump (tests only)
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
    ap.add_argument("--jump", default="")
    ap.add_argument("--jump1", default="")
    ap.add_argument("--party", default="NO_FRIEND")
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--extra", action="append", default=[])
    ap.add_argument("--mod", action="append", default=[], help="OpenKH-style mod folder(s) with room script edits")
    ap.add_argument("--order", default="before", choices=["after", "before"])
    ap.add_argument("--rooms", default="")
    ap.add_argument("--also", default="54")
    ap.add_argument("--override", default=str(OVERRIDES))
    ap.add_argument("--no-twin", action="store_true")
    ap.add_argument("--no-disc", action="store_true")
    a = ap.parse_args()

    var = ROOT / "local" / "variants" / f"s1-{a.name}"
    if var.exists():
        shutil.rmtree(var)
    var.mkdir(parents=True)
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_CLI_HOME=str(ROOT / "local" / "dotnet-home"))
    overlays = [str(pathlib.Path(o).resolve()) for o in a.overlay]

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

    for k, m in enumerate(a.mod):
        # a small OpenKH-style mod folder (mod.yml + script texts): built with the shared tool, used as an overlay
        run([str(DOTNET), str(KH2TOOL), "patch", str(EXTRACT), str(pathlib.Path(m).resolve()), str(var / f"mod{k}")], env)
        overlays.append(str(var / f"mod{k}" / "ard"))

    built = var / "built"
    if a.no_twin:
        (built / "ard").mkdir(parents=True)
        for o in overlays:
            for f in pathlib.Path(o).glob("*.ard"):
                shutil.copyfile(f, built / "ard" / f.name)
    else:
        cmd = [str(DOTNET), str(LANEJ), "twin-all", str(ARD), ";".join(overlays) or "-", str(MAP), str(built),
               str(var / "report.csv"), a.order, a.rooms or "-", a.also or "-", a.override or "-"]
        (var / "twin-all.txt").write_text(run(cmd, env))
    for x in a.extra:
        for f in pathlib.Path(x).glob("*.ard"):
            shutil.copyfile(f, built / "ard" / f.name)
            print("extra room file:", f.name)
    if a.no_disc:
        return
    iso = ROOT / "local" / "iso" / f"test-s1-{a.name}.iso"
    run([str(DOTNET), str(KH2TOOL), "inject", str(BUILD3), str(iso), str(built), str(var / "inject-report.txt")], env)
    print("disc:", iso)


if __name__ == "__main__":
    main()
