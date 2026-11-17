"""Build the two-player disc v5 = build_disc_v4.py + A SECOND COPY OF THE SPECIAL PLAYER OBJECTS (seventh round):
the rooms that place a special player object directly (no PLAYER placeholder: lane F's "not handled" list of 21
placements in al05, al14, tr02, po06, eh22, nm10) get a second copy beside it, so player 2 has a hero there too.
  - lane F's placement tool gets the objects of --special in its "also" list (default: see SPECIAL below);
  - tools/own/sp_swap.py then exchanges the two records of every such pair, so the ORIGINAL object is built
    first and stays the engine's player (player 1); the added copy is player 2's.
Which objects are in the default list, and why the others are not, is written in docs/STATE.md, seventh round,
part 7e. --special - gives a v4 disc again.
Everything else is build_disc_v4.py's (its text follows).

Build the two-player disc v4 = build_disc_v3.py + A SECOND SKATEBOARD EVERYWHERE:
  - tools/boards/Boards clone-all writes a second board beside every placed skateboard of the game (147 places in
    29 rooms: every free-roam board, the two Mail Delivery groups of tt06, the boards of the five skate
    challenges), with lane F's ground check; report: boards-report.csv;
  - tools/boards/make_skate.py changes the eight mission scripts that put the player on a board at their start
    (Mail Delivery x3, AL00 / CA02 / HB09 / NM09 / TT07 _SKATE_01): the twin is put on the second board.
This replaces v3's make_mail.py steps (--no-mail is now --no-boards). The rest of this text is build_disc_v2.py's.

Build the two-player disc WITH the boss HP change (merged build 4 and later).

  python -I tools/merge/build_disc_v4.py <outIsoName> [--no-boards] [--boss-percent 75] [--capped] [--overlay DIR ...]
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
BOARDS = ROOT / "local" / "build" / "boards" / "Boards.dll"
SKATE = ROOT / "tools" / "boards" / "make_skate.py"
BOARD_OBJS = "5AB,81A,8C0,8C1,8C2,8C3,8C4"
SWAP = ROOT / "tools" / "own" / "sp_swap.py"
SPECIAL = "35B,4FF,5F5"          # second copies: the Pooh flight, the carpet rider, the light cycle
SPECIAL_PLAYERS = "35B,3C8,4FF,5E9,5F5,840"   # of these (when in --special) the original is made the first one built

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
    ap.add_argument("--jump1", default="", help='TEST DISCS ONLY: "WORLD AREA ENTRANCE", a Type 1 jump (free roam)')
    ap.add_argument("--mod", action="append", default=[], help="TEST DISCS ONLY: OpenKH-style mod folder(s) with room script edits")
    ap.add_argument("--party", default="NO_FRIEND")
    ap.add_argument("--base", default=str(BUILD3))
    ap.add_argument("--no-boards", action="store_true")
    ap.add_argument("--special", default=SPECIAL, help="object numbers (hex) that get a second copy; - = none (disc v4)")
    a = ap.parse_args()

    stem = pathlib.Path(a.name).stem
    var = ROOT / "local" / "variants" / ("v5-" + stem)
    if var.exists():
        shutil.rmtree(var)
    var.mkdir(parents=True)
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_CLI_HOME=str(ROOT / "local" / "dotnet-home"))
    overlays = [str(pathlib.Path(o).resolve()) for o in a.overlay]
    for k, m in enumerate(a.mod):
        run([str(DOTNET), str(KH2TOOL), "patch", str(EXTRACT), str(pathlib.Path(m).resolve()), str(var / f"mod{k}")], env)
        overlays.append(str(var / f"mod{k}" / "ard"))
    boards = not a.no_boards and not a.no_twin
    if boards:
        cmd = [str(DOTNET), str(BOARDS), "clone-all", str(ARD), ";".join(overlays) or "-", str(MAP),
               str(var / "boards"), str(var / "boards-report.csv"), BOARD_OBJS, "m_", "tt06:b_40,tt06:b_43"]
        (var / "clone-all.txt").write_text(run(cmd, env))
        overlays.append(str(var / "boards" / "ard"))
    if a.jump1:
        mod = var / "mod"
        mod.mkdir()
        (mod / "mod.yml").write_text(MOD_YML)
        world, area, entrance = a.jump1.split()
        lines = ["Program 0x34"]
        if a.party != "-":
            lines.append(f"Party {a.party}")
        lines += ["Bgm Default Default", "AreaSettings 0 -1",
                  f" SetJump Type 1 World {world} Area {area} Entrance {entrance} LocalSet 0 FadeType 16386",
                  " SetPartyMenu 0", ""]
        (mod / "tt01_evt.txt").write_text(chr(10).join(lines))
        run([str(DOTNET), str(KH2TOOL), "patch", str(EXTRACT), str(mod), str(var / "jump")], env)
        overlays.append(str(var / "jump" / "ard"))
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
        if rooms and (a.jump or a.jump1) and "tt01" not in rooms.split(","):
            rooms += ",tt01"
        cmd = [str(DOTNET), str(LANEF), "twin-all", str(ARD), ";".join(overlays) or "-", str(MAP),
               str(built), str(var / "report.csv"), "before", rooms or "-",
               ",".join(x for x in (a.also, "" if a.special == "-" else a.special) if x and x != "-") or "-"]
        (var / "twin-all.txt").write_text(run(cmd, env))
        if a.special != "-":
            players = ",".join(x for x in SPECIAL_PLAYERS.split(",") if x in a.special.split(","))
            if players:
                (var / "sp-swap.txt").write_text(run([sys.executable, "-I", str(SWAP), str(built / "ard"), str(var / "swap"), players], env))
                for f in sorted((var / "swap").glob("*.ard")):
                    shutil.copyfile(f, built / "ard" / f.name)
        for o in overlays:      # with --rooms the placement tool only writes those rooms; the jump recipe must go in
            for f in sorted(pathlib.Path(o).glob("*.ard")):
                if not (built / "ard" / f.name).exists():
                    (built / "ard").mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, built / "ard" / f.name)

    if boards:
        run([sys.executable, "-I", str(SKATE), str(built), str(var / "report.csv"), str(var / "boards-report.csv")], env)

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
