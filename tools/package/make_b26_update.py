r"""One-off (STATE part 140, after edit_package_v26.py and make_test_package.py --rebuild): the Desktop folder
PS2-ONLINE-KH2-TEST-b24 becomes a complete BUILD 26 (card1 exe, the build 26 read-me from dist, START-HERE "BUILDS 13 TO 26"),
and Desktop\PS2-ONLINE-KH2-TEST-b26-UPDATE(.zip) is written with the same files for the second PC.
  - "READ-ME (BUILD 25 UPDATE).txt" is removed from the Desktop folder; "READ-ME (BUILD 26 UPDATE).txt" takes its place;
  - the package id is computed like make_test_package.py (program files; START-HERE left out) over the folder as it is then;
  - package-id.txt and the "Package:" line of START-HERE get that id.
  python -I tools/package/make_b26_update.py
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
UPD = DESK / "PS2-ONLINE-KH2-TEST-b26-UPDATE"
CARD1 = ROOT / "emulator-src" / "builds" / "card1" / "pcsx2-qtx64.exe"
DIST_README = ROOT / "dist" / "PS2-ONLINE-KH2-TEST" / "1-READ-ME-FIRST (KH2 TEST).txt"
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings", "debuggerlayouts", "cheats"}
START = "START-HERE (TWO PCs AT HOME).txt"
OLD_UPDATE = "READ-ME (BUILD 25 UPDATE).txt"
UPDATE_README = "READ-ME (BUILD 26 UPDATE).txt"
SHIP = [r"emulator\pcsx2-qtx64.exe", "package-id.txt", "1-READ-ME-FIRST (KH2 TEST).txt", START, UPDATE_README]

UPDATE_TEXT = r"""KH2 TWO-PLAYER TEST - BUILD 26 UPDATE (the memory card travels with the game)
=============================================================================
Build 26 = build 25 + a new emulator program (emulator\pcsx2-qtx64.exe) + the read-me texts of build 26.
The disc file, the patch files and your settings are NOT changed.
What is new: read "NEW IN BUILD 26" at the top of 1-READ-ME-FIRST (KH2 TEST).txt. In short: when the friend joins
with another memory card, the host's card is sent to him before the game starts; his own card is kept as a backup
(emulator\memcards\Mcd001-backup-<date>.ps2). WHOEVER HOSTS DECIDES THE CARD: host on the PC that has your saves.

HOW TO PUT IT IN (BOTH PCs)
1. Close the game and the launcher.
2. Copy EVERYTHING in this update (the folder "emulator" and the four text files) into your KH2 test folder
   (the folder with START-KH2-TEST.bat). Say YES to replace.
   You may delete "READ-ME (BUILD 25 UPDATE).txt" there; it is replaced by this file.
3. Open package-id.txt on both PCs: the two numbers must be the same (the one in this update).
   BOTH PCs need build 26: a PC with build 25 is refused when it joins ("Different version of the online emulator").
4. Start as always (START-KH2-TEST.bat), Host / Join as always. No need to copy the memory card any more.
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


assert "TEST BUILD 26" in DIST_README.read_text(encoding="utf-8"), "run edit_package_v26.py and make_test_package.py --rebuild first"
shutil.copy2(CARD1, FOLDER / "emulator" / "pcsx2-qtx64.exe")
shutil.copy2(DIST_README, FOLDER / "1-READ-ME-FIRST (KH2 TEST).txt")
if (FOLDER / OLD_UPDATE).exists():
    (FOLDER / OLD_UPDATE).unlink()
(FOLDER / UPDATE_README).write_bytes(UPDATE_TEXT.replace("\n", "\r\n").encode("utf-8"))
files = program_files(FOLDER)
new_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
(FOLDER / "package-id.txt").write_text(
    f"PS2 Online KH2 TEST package {new_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
    "Every player must have the same package id.\r\n"
    "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n", newline="")
lines = (FOLDER / START).read_bytes().decode("utf-8").split("\r\n")
idx = [i for i, l in enumerate(lines) if l.startswith("Package: PS2 Online KH2 TEST package ")]
bld = [i for i, l in enumerate(lines) if "BUILDS 13 TO 25 KEEP THAT DISC FILE" in l or "BUILDS 13 TO 26 KEEP THAT DISC FILE" in l]
assert len(idx) == 1 and len(bld) == 1
lines[idx[0]] = f"Package: PS2 Online KH2 TEST package {new_id}"
lines[bld[0]] = lines[bld[0]].replace("BUILDS 13 TO 25", "BUILDS 13 TO 26")
(FOLDER / START).write_bytes("\r\n".join(lines).encode("utf-8"))
if UPD.exists():
    shutil.rmtree(UPD)
for rel in SHIP:
    (UPD / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FOLDER / rel, UPD / rel)
z = DESK / "PS2-ONLINE-KH2-TEST-b26-UPDATE.zip"
if z.exists():
    z.unlink()
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for rel in SHIP:
        zf.write(UPD / rel, rel.replace("\\", "/"))
assert program_files(FOLDER) == files
assert sha(FOLDER / "emulator" / "pcsx2-qtx64.exe", "sha1") == sha(CARD1, "sha1")
print("build 26 package id", new_id, "| exe sha1", sha(CARD1, "sha1"))
print("zip", z, round(z.stat().st_size / 1e6, 1), "MB:", zipfile.ZipFile(z).namelist())
