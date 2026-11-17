"""After make_test_package.py: make the host's test folder complete for TWO PCs OF THE SAME OWNER (user decision
2026-11-12: player 2 is the user's own second PC, not a friend).
  - the two-player disc file (local/iso/kh2-coop-v5.iso, check number below) goes into the folder's MY-GAMES under
    the name the launcher expects; an existing file with the right size is checked, not copied again;
  - "START-HERE (TWO PCs AT HOME).txt" (tools/package/kit) is written into dist and into the folder, with the
    package id and this PC's home network address filled in.
The whole folder can then be copied to the second PC as it is. Nothing outside <project>/dist is written.
  python -I tools/package/finish_two_pcs.py [--no-check]
"""
import hashlib
import pathlib
import shutil
import socket
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "dist" / "PS2-ONLINE-KH2-TEST"
SRC = ROOT / "local" / "iso" / "kh2-coop-v5.iso"
DST = OUT / "MY-GAMES (never share)" / "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso"
OLD = [OUT / "MY-GAMES (never share)" / ("Kingdom Hearts II - Final Mix (2 Players TEST v%d).iso" % n) for n in (1, 2, 3, 4)]
CHECK = "c0d652c46c603c093653d58f2506503a5089ce9c"
TEXT = "START-HERE (TWO PCs AT HOME).txt"


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


assert OUT.is_dir(), "run make_test_package.py first"
for old in OLD:                     # only ONE Kingdom Hearts file may sit in MY-GAMES (the dist folder is ours)
    if old.exists():
        old.unlink()
        print("removed the older two-player disc file:", old.name)
if not DST.exists() or DST.stat().st_size != SRC.stat().st_size:
    print("copying the disc file (4.3 GB) ...")
    shutil.copyfile(SRC, DST)
else:
    print("disc file already there")
if "--no-check" not in sys.argv:
    got = sha1(DST)
    assert got == CHECK, "disc file check number is %s" % got
    print("disc file check number OK:", got)
others = [p.name for p in DST.parent.iterdir() if p.name != DST.name]
assert not others, "other files in MY-GAMES: %r" % others

ips = [a for a in socket.gethostbyname_ex(socket.gethostname())[2]
       if a.startswith("192.168.") or a.startswith("10.") or (a.startswith("172.") and 16 <= int(a.split(".")[1]) <= 31)]
ip = ips[0] if ips else "(not found: use ipconfig)"
package = (OUT / "package-id.txt").read_text(encoding="utf-8").splitlines()[0]
text = (ROOT / "tools" / "package" / "kit" / TEXT).read_text(encoding="utf-8")
text = text.replace("{PACKAGE}", package).replace("{FOLDER}", str(OUT)).replace("{IP}", ip)
for place in (ROOT / "dist", OUT):
    (place / TEXT).write_text(text, encoding="utf-8", newline="\r\n")
print("written", TEXT, "| package:", package, "| address:", ip)
