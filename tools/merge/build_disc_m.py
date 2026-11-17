"""Merge lane: build a disc copy for the merged build.

  python -I tools/merge/build_disc_m.py <outIsoName> [--overlay DIR ...] [--no-twin] [--order before|after]
                                        [--rooms tt07,ca02] [--base FILE]

  <outIsoName>  file name inside local/iso, for example kh2-coop-v1.iso or test-m-roam.iso
  --overlay     folder(s) with *.ard files that replace the stock ones first (test "jump" recipes of lane B / F)
  --no-twin     do not add twins (only the overlay goes in): the "one player alone" discs
  --base        disc image to copy (default: the English text build 3 candidate)

Steps: lane F's tool (local/build/lane-f/LaneF.dll twin-all, run as it is) adds a second PLAYER placeholder beside
every placeholder; the shared tool Kh2Tool inject writes the room files into a COPY of the base image.
The base image, the original disc and the other lanes' files are only read. Same inputs give the same bytes.
Work files and reports: local/variants/m-<name>/.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
LANEF = ROOT / "local" / "build" / "lane-f" / "LaneF.dll"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
BUILD3 = ROOT / "local" / "iso" / "English text build3 (candidate).iso"
ARD = ROOT / "local" / "extract" / "kh2" / "ard"
MAP = ROOT / "local" / "extract" / "kh2" / "map" / "jp"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--no-twin", action="store_true")
    ap.add_argument("--order", default="before", choices=["after", "before"])
    ap.add_argument("--rooms", default="")
    ap.add_argument("--also", default="54")
    ap.add_argument("--base", default=str(BUILD3))
    a = ap.parse_args()

    stem = pathlib.Path(a.name).stem
    var = ROOT / "local" / "variants" / ("m-" + stem)
    if var.exists():
        shutil.rmtree(var)
    (var / "built" / "ard").mkdir(parents=True)
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_CLI_HOME=str(ROOT / "local" / "dotnet-home"))
    overlays = [pathlib.Path(o).resolve() for o in a.overlay]
    if a.no_twin:
        for o in overlays:
            for f in sorted(o.glob("*.ard")):
                shutil.copyfile(f, var / "built" / "ard" / f.name)
        print("no twins; overlay files:", sorted(p.name for p in (var / "built" / "ard").iterdir()))
    else:
        shutil.rmtree(var / "built")
        cmd = [str(DOTNET), str(LANEF), "twin-all", str(ARD), ";".join(map(str, overlays)) or "-", str(MAP),
               str(var / "built"), str(var / "report.csv"), a.order, a.rooms or "-", a.also or "-"]
        out = subprocess.run(cmd, env=env, capture_output=True, text=True)
        print(out.stdout.strip())
        if out.returncode:
            sys.exit(out.stderr)
        (var / "twin-all.txt").write_text(out.stdout)
    iso = ROOT / "local" / "iso" / a.name
    out = subprocess.run([str(DOTNET), str(KH2TOOL), "inject", a.base, str(iso), str(var / "built"),
                          str(var / "inject-report.txt")], env=env, capture_output=True, text=True)
    print(out.stdout.strip())
    if out.returncode:
        sys.exit(out.stderr)
    print("disc:", iso)


if __name__ == "__main__":
    main()
