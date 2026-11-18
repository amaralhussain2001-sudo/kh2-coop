"""One-off (STATE part 139): the BUILD 25 UPDATE for the user's two PCs = build 24 + emulator-src/builds/pace1 (frame pacing fix).
Writes Desktop/PS2-ONLINE-KH2-TEST-b25-UPDATE/ and its .zip; reads the Desktop b24 folder (never writes it). The package id is
make_test_package.py's method (program files without START-HERE, which finish_two_pcs.py adds after the id); it asserts that the
method reproduces build 24's id first. Already run 2026-11-17 19:46 (id 21d226082015); running it again rewrites the same files
ONLY while the b24 folder still holds the b24 exe (else the assert stops it).
  python -I tools/package/make_b25_update.py
"""
import hashlib, json, pathlib, shutil, time, zipfile
B24 =pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2-TEST-b24")
NEW = pathlib.Path(r"C:\Users\PC FORCE\Desktop\New folder (3)\emulator-src\builds\pace1\pcsx2-qtx64.exe")
UPD = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2-TEST-b25-UPDATE")
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings", "debuggerlayouts", "cheats"}
EXE = r"emulator\pcsx2-qtx64.exe"
def sha(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
files = {}
for p in sorted(B24.rglob("*")):
    if not p.is_file(): continue
    rel = p.relative_to(B24); parts = rel.parts
    if parts[0] in ("logs", GAMES) or rel.name in ("my-settings.txt", "package-id.txt", "game-file-checks.txt",
                                                    "game-file-check.pnach", "START-HERE (TWO PCs AT HOME).txt"): continue
    if parts[0] == "emulator" and len(parts) > 1 and parts[1] in USER_DIRS | RUNTIME_DIRS: continue
    files[str(rel)] = sha(p, "sha256")
old_id = (B24 / "package-id.txt").read_text().split()[5]
assert hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12] == old_id, "id method"
files[EXE] = sha(NEW, "sha256")
new_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
exe_sha1 = sha(NEW, "sha1")
if UPD.exists(): shutil.rmtree(UPD)
(UPD / "emulator").mkdir(parents=True)
shutil.copy2(NEW, UPD / "emulator" / "pcsx2-qtx64.exe")
(UPD / "package-id.txt").write_text(
    f"PS2 Online KH2 TEST package {new_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
    "Every player must have the same package id.\r\n"
    "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n", newline="")
readme = rf"""KH2 TWO-PLAYER TEST - BUILD 25 UPDATE (smoother frame rate online)
===================================================================
Build 25 = build 24 + ONE new file: emulator\pcsx2-qtx64.exe (the emulator program).
The disc file, the patch files, the memory card and your settings are NOT changed.

WHAT IT FIXES
When one PC is a little slower than the other (or the internet is uneven), the faster PC had to wait for it many
times a second and then ran fast to win the time back. The frame rate jumped up and down. Now the faster PC just
follows the slower PC's pace, smoothly. Only the timing on your PC changes; the game itself is not changed.
Test on one PC with a copy that runs 1 % slow: the faster copy waited 1,488 times (19.3 s in 100 s) with build 24,
119 times (0.6 s) with build 25, the same game speed, never out of sync.
It cannot make the slower PC faster: if one PC cannot hold 60 fps, choose the same lower Picture on both (3x).

HOW TO PUT IT IN (BOTH PCs)
1. Close the game and the launcher.
2. Copy the folder "emulator" and the file "package-id.txt" from this update into your KH2 test folder
   (the folder with START-KH2-TEST.bat). Say YES to replace.
     First PC:  Desktop\PS2-ONLINE-KH2-TEST-b24
     Second PC: its KH2 test folder (D:\Games\PS2-ONLINE in your last logs)
3. package-id.txt must now say {new_id} on BOTH PCs (build 24 was {old_id}).
   The new emulator\pcsx2-qtx64.exe has the check number (SHA-1) {exe_sha1}
4. Start as always (START-KH2-TEST.bat), Host / Join as always.

AFTER PLAYING: send the "logs" folder of BOTH PCs again, and from the SECOND PC also emulator\logs\emulog.txt
(it names that PC's graphics card; needed for the "OUT OF SYNC" message your last session showed from the start).
"""
(UPD / "READ-ME (BUILD 25 UPDATE).txt").write_text(readme.replace("\n", "\r\n"), encoding="utf-8", newline="")
z = UPD.parent / "PS2-ONLINE-KH2-TEST-b25-UPDATE.zip"
if z.exists(): z.unlink()
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for p in sorted(UPD.rglob("*")):
        if p.is_file(): zf.write(p, p.relative_to(UPD))
print("build 24 id", old_id, "-> build 25 id", new_id, "| exe sha1", exe_sha1)
print("zip", z, round(z.stat().st_size / 1e6, 1), "MB")
with zipfile.ZipFile(z) as zf: print(zf.namelist())
