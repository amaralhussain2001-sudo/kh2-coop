r"""One-off (STATE part 146, after edit_package_v30.py, make_package_patch.py and make_test_package.py --rebuild): the Desktop folder
PS2-ONLINE-KH2-TEST-b24 becomes a complete BUILD 30 (the build 30 patch files, launcher and read-me from dist, the card1 exe,
START-HERE "BUILDS 13 TO 30"), and Desktop\PS2-ONLINE-KH2-TEST-b30-UPDATE(.zip) is written with the same files for the second PC.
  - older "READ-ME (BUILD 2x UPDATE).txt" files are removed from the Desktop folder; "READ-ME (BUILD 30 UPDATE).txt" takes their place;
  - the package id is computed like make_test_package.py (program files; START-HERE left out) over the folder as it is then;
  - package-id.txt and the "Package:" line of START-HERE get that id.
  python -I tools/package/make_b30_update.py
"""
import hashlib
import json
import pathlib
import shutil
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DESK = pathlib.Path(r"C:\Users\PC FORCE\Desktop")
FOLDER = DESK / "PS2-ONLINE-KH2-TEST-b24"
UPD = DESK / "PS2-ONLINE-KH2-TEST-b30-UPDATE"
DIST = ROOT / "dist" / "PS2-ONLINE-KH2-TEST"
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings", "debuggerlayouts", "cheats"}
START = "START-HERE (TWO PCs AT HOME).txt"
OLD_UPDATES = ["READ-ME (BUILD 25 UPDATE).txt", "READ-ME (BUILD 26 UPDATE).txt", "READ-ME (BUILD 27 UPDATE).txt",
               "READ-ME (BUILD 28 UPDATE).txt", "READ-ME (BUILD 29 UPDATE).txt"]
UPDATE_README = "READ-ME (BUILD 30 UPDATE).txt"
FROM_DIST = [r"emulator\pcsx2-qtx64.exe", r"emulator\patches\SLPM-66675_F266B00B.pnach",
             r"SHARED-SCREEN-FALLBACK\SLPM-66675_F266B00B.pnach", "1-READ-ME-FIRST (KH2 TEST).txt", r"launcher\Launcher.ps1"]
SHIP = FROM_DIST + ["package-id.txt", START, UPDATE_README]

UPDATE_TEXT = r"""KH2 TWO-PLAYER TEST - BUILD 30 UPDATE (a destroyed Light Cycle comes back)
==========================================================================
Build 30 = build 29 + a new KH2 patch file (emulator\patches\SLPM-66675_F266B00B.pnach and its shared-screen copy in
SHARED-SCREEN-FALLBACK) + the read-me texts of build 30. The emulator program and the launcher are build 28's (both are in this
update too, so a PC that missed an update is complete after it). The disc file, the memory card and your settings are NOT changed.
What is new: read "NEW IN BUILD 30" (and "NEW IN BUILD 29") at the top of 1-READ-ME-FIRST (KH2 TEST).txt. In short:
  build 30: on the Light Cycle a destroyed cycle comes back after about 5 seconds; the ride ends only when both are down.
  build 29: player 2's Summon plays its entrance movie too.

HOW TO PUT IT IN (BOTH PCs)
1. Close the game and the launcher.
2. Copy EVERYTHING in this update (the folders "emulator", "launcher" and "SHARED-SCREEN-FALLBACK" and the four text files)
   into your KH2 test folder (the folder with START-KH2-TEST.bat). Say YES to replace.
   You may delete older "READ-ME (BUILD 2x UPDATE).txt" files there.
3. Open package-id.txt on both PCs: the two numbers must be the same (the one in this update).
   BOTH PCs need build 30: with different patch files the join is refused ("Different patch files").
4. Start as always. Host on the PC that has your saves (the host's memory card goes to the other PC, since build 26).
"""


def sha(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def program_files(root):
    out = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        parts = rel.parts
        if parts[0] in ("logs", GAMES) or rel.name in ("my-settings.txt", "package-id.txt", "game-file-checks.txt",
                                                        "game-file-check.pnach", START):
            continue
        if parts[0] == "emulator" and len(parts) > 1 and parts[1] in USER_DIRS | RUNTIME_DIRS:
            continue
        out[str(rel)] = sha(p, "sha256")
    return out


assert "TEST BUILD 30" in (DIST / "1-READ-ME-FIRST (KH2 TEST).txt").read_text(encoding="utf-8"), "rebuild dist first"
for rel in FROM_DIST:
    shutil.copy2(DIST / rel, FOLDER / rel)
for old in OLD_UPDATES:
    if (FOLDER / old).exists():
        (FOLDER / old).unlink()
(FOLDER / UPDATE_README).write_bytes(UPDATE_TEXT.replace("\n", "\r\n").encode("utf-8"))
files = program_files(FOLDER)
new_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
(FOLDER / "package-id.txt").write_text(
    f"PS2 Online KH2 TEST package {new_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
    "Every player must have the same package id.\r\n"
    "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n", newline="")
lines = (FOLDER / START).read_bytes().decode("utf-8").split("\r\n")
idx = [i for i, l in enumerate(lines) if l.startswith("Package: PS2 Online KH2 TEST package ")]
bld = [i for i, l in enumerate(lines) if "BUILDS 13 TO 29 KEEP THAT DISC FILE" in l or "BUILDS 13 TO 30 KEEP THAT DISC FILE" in l]
assert len(idx) == 1 and len(bld) == 1
lines[idx[0]] = f"Package: PS2 Online KH2 TEST package {new_id}"
lines[bld[0]] = lines[bld[0]].replace("BUILDS 13 TO 29", "BUILDS 13 TO 30")
(FOLDER / START).write_bytes("\r\n".join(lines).encode("utf-8"))
if UPD.exists():
    shutil.rmtree(UPD)
for rel in SHIP:
    (UPD / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FOLDER / rel, UPD / rel)
z = DESK / "PS2-ONLINE-KH2-TEST-b30-UPDATE.zip"
if z.exists():
    z.unlink()
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for rel in SHIP:
        zf.write(UPD / rel, rel.replace("\\", "/"))
assert program_files(FOLDER) == files
for rel in FROM_DIST:
    assert sha(FOLDER / rel, "sha1") == sha(DIST / rel, "sha1"), rel
print("build 30 package id", new_id)
print("patch sha1", sha(FOLDER / FROM_DIST[1], "sha1"), "| exe sha1", sha(FOLDER / FROM_DIST[0], "sha1"))
print("zip", z, round(z.stat().st_size / 1e6, 1), "MB:", zipfile.ZipFile(z).namelist())
