"""Lane H: build a test disc on the merged-build layout (English build 3, twin record before the placeholder).

Copy of lane J's build_disc.py with lane H names, the build 3 candidate as base, lane J's placement override file
by default, and --move-hero / --move-twin to put one of the two heroes of a room somewhere else (far-apart tests).

  python -I tools/lane-h/build_disc_h.py <name> [--jump "WORLD LOCALSET" | --jump1 "WORLD AREA ENTRANCE"]
         [--party NO_FRIEND|DEFAULT|W_FRIEND|-] [--overlay DIR ...] [--extra DIR ...] [--rooms a,b] [--no-twin]
         [--move-hero "room:x:z:newx:newy:newz"] [--move-twin "room:x:z:newx:newy:newz"]

  <name>        result: local/iso/test-h-<name>.iso, work files in local/variants/h-<name>/
  --jump        New Game jumps (Type 2) to the room that owns program LOCALSET of WORLD (lane B's method)
  --jump1       New Game jumps (Type 1, programs from the fresh save: free roam) to WORLD AREA ENTRANCE
  --overlay     folder(s) with *.ard files that replace the stock ones first (they get twins too)
  --extra       folder(s) with *.ard files that replace the result last (no twin is added to them)
  --move-hero   in the built room file, move the PLAYER placeholder standing at (x, z) (the game's own hero spot)
  --move-twin   in the built room file, move the OTHER placeholder within 200 units of (x, z) (the twin's spot)
The original disc, the English copies and the other lanes' files are only read.
"""
import argparse
import os
import pathlib
import shutil
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
LANEJ = ROOT / "local" / "build" / "lane-j" / "LaneJ.dll"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
BUILD3 = ROOT / "local" / "iso" / "English text build3 (candidate).iso"
OVERRIDE = ROOT / "tools" / "lane-j" / "data" / "overrides.csv"
EXTRACT = ROOT / "local" / "extract" / "kh2"
ARD = EXTRACT / "ard"
MAP = EXTRACT / "map" / "jp"

MOD_YML = """title: lane H jump (tests only)
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
        sys.exit(out.stderr or "command failed: %s" % cmd)
    return out.stdout


def move(path, spec, twin):
    room, x, z, nx, ny, nz = spec.split(":")
    x, z, nx, ny, nz = float(x), float(z), float(nx), float(ny), float(nz)
    f = path / (room + ".ard")
    data = bytearray(f.read_bytes())
    hits = []
    for i in range(0, len(data) - 16, 4):
        if struct.unpack_from("<I", data, i)[0] != 0x236:
            continue
        px, py, pz = struct.unpack_from("<3f", data, i + 4)
        exact = abs(px - x) < 0.2 and abs(pz - z) < 0.2
        near = ((px - x) ** 2 + (pz - z) ** 2) ** 0.5 < 200.0
        if (not twin and exact) or (twin and near and not exact):
            hits.append((i, px, py, pz))
    if len(hits) != 1:
        sys.exit("move: expected one placeholder in %s, found %d: %s" % (room, len(hits), hits))
    i, px, py, pz = hits[0]
    struct.pack_into("<3f", data, i + 4, nx, ny, nz)
    f.write_bytes(data)
    print("moved the %s placeholder of %s from (%.1f, %.1f, %.1f) to (%.1f, %.1f, %.1f)" % (
        "twin" if twin else "hero", room, px, py, pz, nx, ny, nz))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--jump", default="")
    ap.add_argument("--jump1", default="")
    ap.add_argument("--party", default="NO_FRIEND")
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--extra", action="append", default=[])
    ap.add_argument("--rooms", default="")
    ap.add_argument("--also", default="54")
    ap.add_argument("--no-twin", action="store_true")
    ap.add_argument("--move-hero", action="append", default=[])
    ap.add_argument("--move-twin", action="append", default=[])
    a = ap.parse_args()

    var = ROOT / "local" / "variants" / ("h-" + a.name)
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
            jump = " SetJump Type 2 World %s Area 0 Entrance 0 LocalSet %s FadeType 16386" % (world, localset)
        else:
            world, area, entrance = a.jump1.split()
            jump = " SetJump Type 1 World %s Area %s Entrance %s LocalSet 0 FadeType 16386" % (world, area, entrance)
        lines = ["Program 0x34"]
        if a.party != "-":
            lines.append("Party " + a.party)
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
        cmd = [str(DOTNET), str(LANEJ), "twin-all", str(ARD), ";".join(overlays) or "-", str(MAP), str(built),
               str(var / "report.csv"), "before", a.rooms or "-", a.also or "-", str(OVERRIDE)]
        (var / "twin-all.txt").write_text(run(cmd, env))
    for x in a.extra:
        for f in pathlib.Path(x).glob("*.ard"):
            shutil.copyfile(f, built / "ard" / f.name)
            print("extra room file:", f.name)
    for spec in a.move_hero:
        move(built / "ard", spec, False)
    for spec in a.move_twin:
        move(built / "ard", spec, True)
    iso = ROOT / "local" / "iso" / ("test-h-%s.iso" % a.name)
    run([str(DOTNET), str(KH2TOOL), "inject", str(BUILD3), str(iso), str(built), str(var / "inject-report.txt")], env)
    print("disc:", iso)


if __name__ == "__main__":
    main()
