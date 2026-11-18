r"""The user's words 2026-11-18: "i dont know which version my second pc has so prepare small winrar to send to him he already maybe
has build 23 or 24". Writes Desktop\KH2-UPDATE-FOR-SECOND-PC.rar: every file that changed from build 23 on (builds 23 and 24 had
the exe builds\view12, the launcher e245d4df..., patch files only differ; later updates changed exe, both patch files, launcher,
read-mes - see make_b25..b31_update.py), taken from the ONE folder Desktop\PS2-ONLINE-KH2, plus link\ps2net-link.exe and
START-KH2-TEST.bat (unchanged, small, so an older folder is complete too) and a short read-me. Nothing of the user's (disc, BIOS,
memory card, inis, my-settings.txt) goes in. Needs WinRAR (C:\Program Files\WinRAR\Rar.exe).
  python -I tools/package/make_second_pc_rar.py
"""
import hashlib
import pathlib
import shutil
import subprocess
import tempfile

GAME = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE-KH2")
OUT = pathlib.Path(r"C:\Users\PC FORCE\Desktop\KH2-UPDATE-FOR-SECOND-PC.rar")
RAR = pathlib.Path(r"C:\Program Files\WinRAR\Rar.exe")
FILES = [r"emulator\pcsx2-qtx64.exe", r"emulator\patches\SLPM-66675_F266B00B.pnach",
         r"SHARED-SCREEN-FALLBACK\SLPM-66675_F266B00B.pnach", r"launcher\Launcher.ps1", r"link\ps2net-link.exe",
         "START-KH2-TEST.bat", "1-READ-ME-FIRST (KH2 TEST).txt", "START-HERE (TWO PCs AT HOME).txt", "package-id.txt"]
README = "READ-ME (UPDATE FOR THE SECOND PC).txt"

package_id = (GAME / "package-id.txt").read_text(encoding="utf-8").splitlines()[0].split()[-1]
build = (GAME / "1-READ-ME-FIRST (KH2 TEST).txt").read_text(encoding="utf-8-sig").splitlines()[0].split("TEST BUILD ")[1].split()[0]
TEXT = f"""KH2 TWO PLAYERS - UPDATE TO THE NEWEST BUILD (build {build}, package {package_id})
==========================================================================
For the SECOND PC. It works on build 23, build 24 or any later build.

1. Close the game and the launcher.
2. Put this rar file INSIDE your KH2 folder (the folder with START-KH2-TEST.bat,
   for example PS2-ONLINE-KH2-TEST-b24).
3. Right-click the rar file > "Extract Here". Say YES TO ALL when it asks to replace files.
4. Open package-id.txt in the folder: it must say {package_id}, the same as on the first PC.
5. Start as always. Host the game on the FIRST PC (its memory card with your saves goes to
   the second PC when you join).

Not touched: your disc file, BIOS, memory card and settings.
What is new: "1-READ-ME-FIRST (KH2 TEST).txt" (the newest builds are at the top).
You can delete the rar file and any old "READ-ME (BUILD 2x UPDATE).txt" files afterwards.
"""


def sha1(p):
    return hashlib.sha1(p.read_bytes()).hexdigest()


assert RAR.exists(), "WinRAR is not installed"
with tempfile.TemporaryDirectory() as tmp:
    stage = pathlib.Path(tmp) / "u"
    for rel in FILES:
        (stage / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GAME / rel, stage / rel)
    (stage / README).write_bytes(TEXT.replace("\n", "\r\n").encode("utf-8"))
    if OUT.exists():
        OUT.unlink()
    subprocess.run([str(RAR), "a", "-r", "-m5", "-ep1", "-idq", str(OUT), str(stage) + "\\*"], check=True)
    check = pathlib.Path(tmp) / "x"
    check.mkdir()
    subprocess.run([str(RAR), "x", "-idq", str(OUT), str(check) + "\\"], check=True)
    got = sorted(str(p.relative_to(check)) for p in check.rglob("*") if p.is_file())
    assert got == sorted(FILES + [README]), got
    for rel in FILES:
        assert sha1(check / rel) == sha1(GAME / rel), rel
print("written", OUT, round(OUT.stat().st_size / 1e6, 1), "MB, package", package_id)
for rel in FILES + [README]:
    print("  ", rel)
