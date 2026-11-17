"""Make the two throw-away copies the dress rehearsal needs (tools/package/rehearse.py):
  local/kit-test-t/A  = the host: a copy of dist/PS2-ONLINE-KH2-TEST
  local/kit-test-t/B  = the friend: a copy of the user's PS2-ONLINE folder (program files and BIOS only, read-only
                        source) with dist/KH2-TEST-FRIEND-KIT.zip unzipped over it and no memory card
Both get the two-player disc (local/iso/kh2-coop-v5.iso) under the package's file name in MY-GAMES; the disc
maker itself is not run here (it was rehearsed when the disc patch was made; the disc has not changed).
Everything is written under local/kit-test-t only. local/ is private and never shared.

  python -I tools/package/make_rehearsal_copies.py
"""
import pathlib
import shutil
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SRC = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE")          # read only
DIST = ROOT / "dist"
KIT = ROOT / "local" / "kit-test-t"
DISC = ROOT / "local" / "iso" / "kh2-coop-v5.iso"
DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso"
GAMES = "MY-GAMES (never share)"


def main():
    for need in (DIST / "PS2-ONLINE-KH2-TEST", DIST / "KH2-TEST-FRIEND-KIT.zip", DISC, SRC):
        if not need.exists():
            sys.exit("missing: %s" % need)
    if KIT.exists():
        shutil.rmtree(KIT)
    A, B = KIT / "A", KIT / "B"
    # A: the host's test folder as built
    shutil.copytree(DIST / "PS2-ONLINE-KH2-TEST", A, ignore=shutil.ignore_patterns("*.iso"))
    # B: the friend's own package (no games, no saves, no logs), then the kit over it
    skip_dirs = {"logs", "memcards", "sstates", "snaps", "cache", "videos"}

    def ignore(folder, names):
        p = pathlib.Path(folder)
        out = []
        for n in names:
            if p == SRC and n == GAMES:
                out.append(n)
            elif (p / n).is_dir() and n.lower() in skip_dirs:
                out.append(n)
            elif n.lower().endswith((".iso", ".chd", ".bin", ".ps2")):
                out.append(n)
        return out

    shutil.copytree(SRC, B, ignore=ignore)
    with zipfile.ZipFile(DIST / "KH2-TEST-FRIEND-KIT.zip") as z:
        z.extractall(B)
    for c in (A, B):
        (c / GAMES).mkdir(exist_ok=True)
        shutil.copy2(DISC, c / GAMES / DISC_NAME)
        for card in (c / "emulator" / "memcards").glob("*.ps2") if (c / "emulator" / "memcards").exists() else []:
            card.unlink()
        (c / "emulator" / "memcards").mkdir(parents=True, exist_ok=True)
        ids = (c / "package-id.txt").read_text(encoding="utf-8", errors="replace").strip() if (c / "package-id.txt").exists() else "?"
        print("%s: package id %s, disc %d bytes" % (c.name, ids, (c / GAMES / DISC_NAME).stat().st_size))


if __name__ == "__main__":
    main()
