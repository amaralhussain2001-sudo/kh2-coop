r"""One-off (STATE part 139, after edit_package_v25.py): the Desktop folder PS2-ONLINE-KH2-TEST-b24 is made a complete BUILD 25
(pace1 exe + the build 25 read-me texts) and the update zip is written again with the same files, so both PCs end identical.
  - "READ-ME (BUILD 25 UPDATE).txt" gets a text without a package id (the id counts that file, so it cannot name itself);
  - the package id is computed like make_test_package.py (program files; START-HERE left out) over the folder as it is then;
  - package-id.txt and the "Package:" line of START-HERE get that id;
  - Desktop\PS2-ONLINE-KH2-TEST-b25-UPDATE(.zip) is written again: exe, package-id.txt, the two read-mes, START-HERE.
  python -I tools/package/make_b25_update2.py
"""
import hashlib
import json
import pathlib
import shutil
import time
import zipfile

DESK = pathlib.Path(r"C:\Users\PC FORCE\Desktop")
FOLDER = DESK / "PS2-ONLINE-KH2-TEST-b24"
UPD = DESK / "PS2-ONLINE-KH2-TEST-b25-UPDATE"
PACE1 = pathlib.Path(__file__).resolve().parent.parent.parent / "emulator-src" / "builds" / "pace1" / "pcsx2-qtx64.exe"
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings", "debuggerlayouts", "cheats"}
START = "START-HERE (TWO PCs AT HOME).txt"
UPDATE_README = "READ-ME (BUILD 25 UPDATE).txt"
SHIP = [r"emulator\pcsx2-qtx64.exe", "package-id.txt", "1-READ-ME-FIRST (KH2 TEST).txt", START, UPDATE_README]

UPDATE_TEXT = r"""KH2 TWO-PLAYER TEST - BUILD 25 UPDATE (smoother frame rate online)
===================================================================
Build 25 = build 24 + a new emulator program (emulator\pcsx2-qtx64.exe) + the read-me texts of build 25.
The disc file, the patch files, the memory card and your settings are NOT changed.
What is new: read "NEW IN BUILD 25" at the top of 1-READ-ME-FIRST (KH2 TEST).txt.

HOW TO PUT IT IN (BOTH PCs)
1. Close the game and the launcher.
2. Copy EVERYTHING in this update (the folder "emulator" and the four text files) into your KH2 test folder
   (the folder with START-KH2-TEST.bat). Say YES to replace.
3. Open package-id.txt on both PCs: the two numbers must be the same (the one in this update).
4. Close the game on both PCs and copy the host's emulator\memcards\Mcd001.ps2 to the same place on the other PC
   (two different memory cards give "OUT OF SYNC" about 7 seconds after the start).
5. Start as always (START-KH2-TEST.bat), Host / Join as always.
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


assert sha(FOLDER / "emulator" / "pcsx2-qtx64.exe", "sha1") == sha(PACE1, "sha1"), "the folder does not hold the pace1 exe"
assert "TEST BUILD 25" in (FOLDER / "1-READ-ME-FIRST (KH2 TEST).txt").read_text(encoding="utf-8"), "run edit_package_v25.py first"
(FOLDER / UPDATE_README).write_bytes(UPDATE_TEXT.replace("\n", "\r\n").encode("utf-8"))
files = program_files(FOLDER)
new_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
(FOLDER / "package-id.txt").write_text(
    f"PS2 Online KH2 TEST package {new_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
    "Every player must have the same package id.\r\n"
    "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n", newline="")
st = (FOLDER / START).read_bytes().decode("utf-8")
lines = st.split("\r\n")
idx = [i for i, l in enumerate(lines) if l.startswith("Package: PS2 Online KH2 TEST package ")]
assert len(idx) == 1
lines[idx[0]] = f"Package: PS2 Online KH2 TEST package {new_id}"
(FOLDER / START).write_bytes("\r\n".join(lines).encode("utf-8"))
if UPD.exists():
    shutil.rmtree(UPD)
for rel in SHIP:
    (UPD / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FOLDER / rel, UPD / rel)
z = DESK / "PS2-ONLINE-KH2-TEST-b25-UPDATE.zip"
if z.exists():
    z.unlink()
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for rel in SHIP:
        zf.write(UPD / rel, rel.replace("\\", "/"))
assert program_files(FOLDER) == files
print("build 25 package id", new_id, "| exe sha1", sha(PACE1, "sha1"))
print("zip", z, round(z.stat().st_size / 1e6, 1), "MB:", zipfile.ZipFile(z).namelist())
