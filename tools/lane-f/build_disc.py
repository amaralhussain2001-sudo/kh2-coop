"""Lane F: build a "twin everywhere" disc copy.

Every PLAYER placeholder in every room gets a second PLAYER placeholder beside it (tool LaneF twin-all), then the
changed room files are written into a COPY of the English-text disc (shared tool Kh2Tool inject).
The original disc file and the English copy are only read.

  python -I tools/lane-f/build_disc.py <name> [--overlay DIR ...] [--order after|before] [--rooms tt07,ca02]

  <name>      result: local/iso/test-f-<name>.iso, work files in local/variants/f-<name>/
  --overlay   folder(s) with *.ard files that replace the stock ones first (lane B's test "jump" recipes)
  --order     twin record right after (default) or right before the player's record
  --rooms     only add twins in these rooms (all other rooms stay stock)
  --also      real player objects placed directly by room data that also get a twin (default 54 = Sora, one room)
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
LANEF = ROOT / "local" / "build" / "lane-f" / "LaneF.dll"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
ENGLISH = ROOT / "local" / "iso" / "Kingdom Hearts II - Final Mix (English text).iso"
ARD = ROOT / "local" / "extract" / "kh2" / "ard"
MAP = ROOT / "local" / "extract" / "kh2" / "map" / "jp"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--order", default="after", choices=["after", "before"])
    ap.add_argument("--rooms", default="")
    ap.add_argument("--also", default="54", help="real player objects placed directly that also get a twin (hex, comma separated; '-' = none)")
    ap.add_argument("--no-disc", action="store_true", help="only build the room files and the report")
    a = ap.parse_args()

    var = ROOT / "local" / "variants" / f"f-{a.name}"
    if var.exists():
        shutil.rmtree(var)
    var.mkdir(parents=True)
    env = {"DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1", "DOTNET_CLI_HOME": str(ROOT / "local" / "dotnet-home")}
    import os
    env = dict(os.environ, **env)
    overlays = ";".join(str(pathlib.Path(o).resolve()) for o in a.overlay) or "-"
    cmd = [str(DOTNET), str(LANEF), "twin-all", str(ARD), overlays, str(MAP), str(var / "built"), str(var / "report.csv"), a.order]
    cmd.append(a.rooms or "-")
    cmd.append(a.also or "-")
    out = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(out.stdout.strip())
    if out.returncode:
        sys.exit(out.stderr)
    (var / "twin-all.txt").write_text(out.stdout)
    if a.no_disc:
        return
    iso = ROOT / "local" / "iso" / f"test-f-{a.name}.iso"
    out = subprocess.run([str(DOTNET), str(KH2TOOL), "inject", str(ENGLISH), str(iso), str(var / "built"), str(var / "inject-report.txt")],
                         env=env, capture_output=True, text=True)
    print(out.stdout.strip())
    if out.returncode:
        sys.exit(out.stderr)
    print("disc:", iso)


if __name__ == "__main__":
    main()
