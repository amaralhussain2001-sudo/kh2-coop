r"""Every build from build 31 on (the user's words 2026-11-18: "in my desktop i have a lot of kh2 files just give me one folder
contain the full game instead of doing that"): the ONE full-game folder Desktop\PS2-ONLINE-KH2 gets the newest build in place.
No more Desktop update folders or update zips. Run it after make_package_patch.py and make_test_package.py --rebuild.
  - every program file of dist\PS2-ONLINE-KH2-TEST is copied in (changed ones only), program files that dist does not have any more
    (old update read-mes) are removed; the disc file in MY-GAMES is copied when its size differs (a new disc, as in build 12);
  - the user's things stay as they are: emulator\memcards (saves), inis, bios, logs, my-settings.txt, game-file-checks.txt;
  - package-id.txt is computed like make_test_package.py (program files only) over the folder, START-HERE comes from the kit with
    that id, the folder's path and this PC's home address;
  - the folder's program files must equal dist's afterwards.
  python -I tools/package/update_desktop_folder.py
"""
import hashlib
import json
import pathlib
import shutil
import socket
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FOLDER = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2")
DIST = ROOT / "dist" / "PS2-ONLINE-KH2-TEST"
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings", "debuggerlayouts", "cheats"}
START = "START-HERE (TWO PCs AT HOME).txt"


def sha(path, algo="sha256"):
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
        out[str(rel)] = sha(p)
    return out


assert FOLDER.is_dir(), "the Desktop folder PS2-ONLINE-KH2 is not there"
assert DIST.is_dir(), "run make_test_package.py --rebuild first"
want, have = program_files(DIST), program_files(FOLDER)
changed = [rel for rel in want if have.get(rel) != want[rel]]
gone = [rel for rel in have if rel not in want]
for rel in changed:
    (FOLDER / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DIST / rel, FOLDER / rel)
for rel in gone:
    (FOLDER / rel).unlink()
for disc in (DIST / GAMES).glob("*.iso"):
    mine = FOLDER / GAMES / disc.name
    if not mine.exists() or mine.stat().st_size != disc.stat().st_size:
        print("copying the disc file (4.3 GB) ...")
        mine.parent.mkdir(exist_ok=True)
        shutil.copy2(disc, mine)
        changed.append(str(mine.relative_to(FOLDER)))
files = program_files(FOLDER)
assert files == want, "the folder's program files differ from dist"
new_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
(FOLDER / "package-id.txt").write_text(
    f"PS2 Online KH2 TEST package {new_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
    "Every player must have the same package id.\r\n"
    "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n", newline="")
ips = [a for a in socket.gethostbyname_ex(socket.gethostname())[2]
       if a.startswith("192.168.") or a.startswith("10.") or (a.startswith("172.") and 16 <= int(a.split(".")[1]) <= 31)]
ip = ips[0] if ips else "(not found: use ipconfig)"
text = (ROOT / "tools" / "package" / "kit" / START).read_text(encoding="utf-8")
text = text.replace("{PACKAGE}", "PS2 Online KH2 TEST package " + new_id).replace("{FOLDER}", str(FOLDER)).replace("{IP}", ip)
(FOLDER / START).write_text(text, encoding="utf-8", newline="\r\n")
print("changed:", changed or "nothing")
print("removed:", gone or "nothing")
print("package id", new_id, "| address", ip, "|", FOLDER)
