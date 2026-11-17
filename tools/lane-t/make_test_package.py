"""Build the Kingdom Hearts II two-player TEST package and the friend kit.

Reads (never writes) the user's package C:\\Users\\PC FORCE\\Desktop\\PS2-ONLINE and writes only under <project>\\dist:
  dist\\PS2-ONLINE-KH2-TEST\\      the test folder for THIS PC (program files, the user's own BIOS and controller
                                 settings, an EMPTY MY-GAMES, no memory card)
  dist\\KH2-TEST-FRIEND-KIT.zip   what the friend unzips into a copy of their own PS2-ONLINE folder
                                 (no disc image, no BIOS, no memory card)

  python -I tools/lane-t/make_test_package.py [--rebuild]
--rebuild replaces an existing test folder but keeps its MY-GAMES and logs.
"""
import hashlib
import json
import pathlib
import shutil
import sys
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SRC = pathlib.Path(r"C:\Users\PC FORCE\Desktop\PS2-ONLINE")
KIT = ROOT / "tools" / "lane-t" / "kit"
DIST = ROOT / "dist"
OUT = DIST / "PS2-ONLINE-KH2-TEST"
ZIP = DIST / "KH2-TEST-FRIEND-KIT.zip"
KH2_PNACH = ROOT / "patches" / "lane-t-kh2test" / "SLPM-66675_F266B00B.pnach"
MERGED = ROOT / "patches" / "merged-v2" / "SLPM-66675_F266B00B.pnach"
DISC_PATCH = ROOT / "local" / "lane-t" / "kh2-coop-v1.kh2patch"
DISC_NAME = "Kingdom Hearts II - Final Mix (2 Players TEST v1).iso"
GAMES = "MY-GAMES (never share)"
USER_DIRS = {"inis", "memcards", "snaps", "sstates", "logs", "bios"}
RUNTIME_DIRS = {"cache", "gamesettings", "covers", "textures", "videos", "inputprofiles", "debuggersettings",
                "debuggerlayouts", "cheats"}

# ---------------------------------------------------------------------------------------------------------------
# Changes to the launcher (a copy; the package's own launcher is not touched). Each pair is (old text, new text).
NEW_FUNCS = r'''# TEST PACKAGE: the game file's check number (SHA-1), remembered per file so it is computed once.
$CheckCache = Join-Path $Root "game-file-checks.txt"
function Game-Check([string]$path) {
    $item = Get-Item -LiteralPath $path
    $key = "$($item.Name)|$($item.Length)|$($item.LastWriteTimeUtc.Ticks)"
    if (Test-Path -LiteralPath $CheckCache) {
        foreach ($line in Get-Content -LiteralPath $CheckCache) {
            $p = $line.LastIndexOf("|")
            if ($p -gt 0 -and $line.Substring(0, $p) -eq $key) { return $line.Substring($p + 1) }
        }
    }
    Say "Checking the game file '$($item.Name)' (first time only, up to a minute)..."
    $form.Refresh()
    $hash = (Get-FileHash -Algorithm SHA1 -LiteralPath $path).Hash.ToLower()
    Add-Content -LiteralPath $CheckCache -Value "$key|$hash" -Encoding UTF8
    return $hash
}
function Show-Check([string]$hash) {
    $h = $hash.Substring(0, 16).ToUpper()
    return ($h.Substring(0, 4) + "-" + $h.Substring(4, 4) + "-" + $h.Substring(8, 4) + "-" + $h.Substring(12, 4))
}
function Write-CheckFile([string]$hash) {
    # The emulator compares the patches folder of all players when they join. This small file is not a patch: it
    # only puts the game file's check number into that comparison, so different game files are refused at the join
    # (also when joining by IP, where no join code carries the number).
    $file = Join-Path (Split-Path $EmuExe) "patches\game-file-check.pnach"
    $text = "comment=Written by the launcher before every start. Not a patch.`r`ncomment=game file check $hash`r`n"
    [System.IO.File]::WriteAllText($file, $text, [System.Text.Encoding]::ASCII)
}
# The join code carries a tag: 1 byte layout id, 1 byte flags, 6 bytes game file size and (TEST PACKAGE) the first
# 8 bytes of the game file's check number, so friends start exactly the same file. Two files can have the same
# size: the original Kingdom Hearts II disc and the two-player disc do.
function Make-Tag([int]$layoutId, [int]$flags, [long]$size, [string]$check) { return ("{0:X2}{1:X2}{2:X12}{3}" -f $layoutId, $flags, $size, $check.Substring(0, 16).ToUpper()) }'''

EDITS = [
    ('$form.Text = "PS2 Online"', '$form.Text = "PS2 Online - KH2 two-player TEST"'),
    ('Layout = "3"; Game = ""; Quality = "auto"; Screen = "16:9";', 'Layout = "1"; Game = ""; Quality = "auto"; Screen = "4:3";'),
    ('function Make-Tag([int]$layoutId, [int]$flags, [long]$size) { return ("{0:X2}{1:X2}{2:X12}" -f $layoutId, $flags, $size) }',
     NEW_FUNCS),
    ('    $picture = Apply-Picture\n',
     '    $check = Game-Check $gamePath\n    Write-CheckFile $check\n    $picture = Apply-Picture\n'),
    ('    $lines += "LogFile = $(Join-Path $LogDir "$stamp-game.txt")"\n',
     '    $lines += "LogFile = $(Join-Path $LogDir "$stamp-game.txt")"\n'
     '    if ($Test -and $env:PS2ONLINE_TEST_EXTRA -and (Test-Path -LiteralPath $env:PS2ONLINE_TEST_EXTRA)) { $lines += Get-Content -LiteralPath $env:PS2ONLINE_TEST_EXTRA } # test only (rehearsal bots)\n'),
    ('    Say "Game: $(Split-Path $gamePath -Leaf). Controllers: $($session.LayoutName). Screen: $($session.Screen). Picture: $picture."\n',
     '    Say "Game: $(Split-Path $gamePath -Leaf). Controllers: $($session.LayoutName). Screen: $($session.Screen). Picture: $picture."\n'
     '    Say "Game file check: $(Show-Check $check)  (must be the same on every player\'s PC)"\n'),
    ("    if ($tagHex -notmatch '^[0-9A-F]{16}$') { Say \"This join code is from another package version. Everyone needs the same package.\"; Stop-All; return }",
     "    if ($tagHex -notmatch '^[0-9A-F]{32}$') { Say \"This join code is from another package. Everyone needs this same KH2 TEST folder (see package-id.txt).\"; Stop-All; return }"),
    ('    $size = [Convert]::ToInt64($tagHex.Substring(4), 16)\n',
     '    $size = [Convert]::ToInt64($tagHex.Substring(4, 12), 16)\n    $hostCheck = $tagHex.Substring(16, 16)\n'),
    ('    $game = Get-Games | Where-Object { $_.Length -eq $size } | Select-Object -First 1\n    if (-not $game) {\n',
     '    $game = $null\n'
     '    $sameSize = @(Get-Games | Where-Object { $_.Length -eq $size })\n'
     '    foreach ($g in $sameSize) { if ((Game-Check $g.FullName).Substring(0, 16).ToUpper() -eq $hostCheck) { $game = $g; break } }\n'
     '    if (-not $game -and $sameSize.Count -gt 0) {\n'
     '        Say "Your game file has the right size but NOT the same content as the host\'s (host: $(Show-Check $hostCheck), yours: $(Show-Check (Game-Check $sameSize[0].FullName))). For Kingdom Hearts II both players must make the disc file with MAKE-KH2-DISC and get the same check number."\n'
     '        Stop-All; return\n'
     '    }\n'
     '    if (-not $game) {\n'),
    ('    $tag = Make-Tag $layout.Id (Screen-Flag) (Get-Item $game).Length\n',
     '    $tag = Make-Tag $layout.Id (Screen-Flag) (Get-Item -LiteralPath $game).Length (Game-Check $game)\n'),
    ('function Say([string]$text) { $statusBox.AppendText((Get-Date -Format "HH:mm:ss") + "  " + $text + "`r`n") }\n',
     'function Say([string]$text) {\n'
     '    $line = (Get-Date -Format "HH:mm:ss") + "  " + $text\n'
     '    $statusBox.AppendText($line + "`r`n")\n'
     '    # TEST PACKAGE: also keep what this window said in the logs folder, so the logs tell the whole story\n'
     '    try { Add-Content -LiteralPath (Join-Path $LogDir ((Get-Date -Format "yyyy-MM-dd") + "-launcher.txt")) -Value $line -Encoding UTF8 } catch {}\n'
     '}\n'),
    ("function Handle-HelperLine([string]$line) {\n    $msg = $line -replace '^\\d+ ', ''\n",
     "function Handle-HelperLine([string]$line) {\n"
     "    if (-not $script:Helper) { return } # TEST PACKAGE: nothing is running any more (for example after a refused join)\n"
     "    $msg = $line -replace '^\\d+ ', ''\n"),
    ('if ($Test -like "join:*") { $form.Add_Shown({ $joinBox.Text = $Test.Substring(5); $joinButton.PerformClick() }) } # test only\n',
     'if ($Test -like "join:*") { $form.Add_Shown({ $joinBox.Text = $Test.Substring(5); $joinButton.PerformClick() }) } # test only\n'
     'if ($Test -like "ip:*") { $form.Add_Shown({ $ipBox.Text = $Test.Substring(3); $ipButton.PerformClick() }) } # test only\n'),
]


def patch_launcher(text):
    crlf = "\r\n" in text
    t = text.replace("\r\n", "\n")
    for old, new in EDITS:
        if t.count(old) != 1:
            sys.exit(f"launcher edit: expected exactly one place for: {old[:70]!r} (found {t.count(old)})")
        t = t.replace(old, new)
    return t.replace("\n", "\r\n") if crlf else t


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def program_files(out):
    res = []
    for p in sorted(out.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(out)
        parts = rel.parts
        if parts[0] in ("logs", GAMES) or rel.name in ("my-settings.txt", "package-id.txt", "game-file-checks.txt",
                                                        "game-file-check.pnach"):
            continue
        if parts[0] == "emulator" and len(parts) > 1 and parts[1] in USER_DIRS | RUNTIME_DIRS:
            continue
        res.append(p)
    return res


def patch_lines(path):
    return [l.strip() for l in path.read_text(encoding="ascii").splitlines() if l.startswith("patch=")]


def main():
    rebuild = "--rebuild" in sys.argv
    if not (SRC / "emulator" / "pcsx2-qtx64.exe").exists():
        sys.exit(f"package not found at {SRC}")
    # the shipped KH2 patch must be the merged build plus only the official widescreen group
    kh2 = KH2_PNACH.read_text(encoding="ascii")
    head = kh2.split("[Widescreen 16:9]")[0]
    ours = [l.strip() for l in head.splitlines() if l.startswith("patch=")]
    if ours != patch_lines(MERGED):
        sys.exit("the test package's KH2 patch does not start with exactly the merged-v2 lines")
    keep = None
    if OUT.exists():
        if not rebuild:
            sys.exit(f"{OUT} exists; use --rebuild (keeps its MY-GAMES and logs)")
        keep = DIST / "_keep_tmp"
        if keep.exists():
            shutil.rmtree(keep)
        keep.mkdir()
        for name in (GAMES, "logs"):
            if (OUT / name).exists():
                shutil.move(str(OUT / name), str(keep / name))
        shutil.rmtree(OUT)
    emu = OUT / "emulator"
    emu.mkdir(parents=True)
    for item in (SRC / "emulator").iterdir():
        if item.is_dir():
            if item.name.lower() in USER_DIRS | RUNTIME_DIRS:
                continue
            shutil.copytree(item, emu / item.name)
        else:
            shutil.copy2(item, emu / item.name)
    for d in sorted(USER_DIRS - {"bios"}):
        (emu / d).mkdir(exist_ok=True)
    shutil.copytree(SRC / "emulator" / "bios", emu / "bios")          # the user's own BIOS: this PC only
    shutil.copy2(SRC / "emulator" / "inis" / "PCSX2.ini", emu / "inis" / "PCSX2.ini")  # the user's own controls
    (emu / "portable.txt").write_text("")
    shutil.copy2(KH2_PNACH, emu / "patches" / KH2_PNACH.name)
    pn = sorted(p.name for p in (emu / "patches").glob("*.pnach"))
    if pn != ["SLPM-66675_F266B00B.pnach", "SLUS-21067_568A5C78.pnach"]:
        sys.exit(f"unexpected patch files in the package: {pn}")
    (OUT / "link").mkdir()
    shutil.copy2(SRC / "link" / "ps2net-link.exe", OUT / "link" / "ps2net-link.exe")
    (OUT / "launcher").mkdir()
    src_launcher = (SRC / "launcher" / "Launcher.ps1").read_bytes()
    bom = src_launcher.startswith(b"\xef\xbb\xbf")
    new_launcher = patch_launcher(src_launcher.decode("utf-8-sig"))
    (OUT / "launcher" / "Launcher.ps1").write_bytes((b"\xef\xbb\xbf" if bom else b"") + new_launcher.encode("utf-8"))
    (OUT / "START-KH2-TEST.bat").write_text(
        "@echo off\r\nstart \"\" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%~dp0launcher\\Launcher.ps1\"\r\n",
        newline="")
    readme = (KIT / "1-READ-ME-FIRST (KH2 TEST).txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    (OUT / "1-READ-ME-FIRST (KH2 TEST).txt").write_text(readme.replace("\n", "\r\n"), encoding="utf-8", newline="")
    shutil.copy2(SRC / "1-READ-ME-FIRST.txt", OUT / "PS2-ONLINE general help.txt")
    disc = OUT / "MAKE-KH2-DISC"
    disc.mkdir()
    shutil.copy2(DISC_PATCH, disc / DISC_PATCH.name)
    ps1 = (KIT / "MAKE-KH2-DISC" / "Make-KH2-Disc.ps1").read_text(encoding="ascii").replace("\r\n", "\n")
    ps1 = ps1.replace("@@PATCH_SHA1@@", sha1(DISC_PATCH))
    (disc / "Make-KH2-Disc.ps1").write_text(ps1.replace("\n", "\r\n"), encoding="ascii", newline="")
    bat = (KIT / "MAKE-KH2-DISC" / "MAKE-KH2-DISC.bat").read_text(encoding="ascii").replace("\r\n", "\n")
    (disc / "MAKE-KH2-DISC.bat").write_text(bat.replace("\n", "\r\n"), encoding="ascii", newline="")
    (OUT / GAMES).mkdir()
    (OUT / "logs").mkdir()
    if keep:
        for name in (GAMES, "logs"):
            if (keep / name).exists():
                shutil.rmtree(OUT / name)
                shutil.move(str(keep / name), str(OUT / name))
        shutil.rmtree(keep)
    # settings: the user's own name / picture / connection choices, with the KH2 defaults
    s = {"Quality": "auto", "Name": "Player", "Fullscreen": "False", "Buffer": "smooth"}
    real = SRC / "my-settings.txt"
    if real.exists():
        for line in real.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                if k in s:
                    s[k] = v
    s.update({"Layout": "1", "Game": DISC_NAME, "Screen": "4:3"})
    (OUT / "my-settings.txt").write_bytes(b"\xef\xbb\xbf" + "\r\n".join(f"{k}={v}" for k, v in s.items()).encode("utf-8") + b"\r\n")
    files = {str(p.relative_to(OUT)): sha256(p) for p in program_files(OUT)}
    kit_id = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
    id_text = (f"PS2 Online KH2 TEST package {kit_id}\r\nbuilt {time.strftime('%Y-%m-%d %H:%M')}\r\n"
               "Every player must have the same package id.\r\n"
               "This is NOT the normal PS2-ONLINE package: it is a separate test folder for Kingdom Hearts II, two players.\r\n")
    (OUT / "package-id.txt").write_text(id_text, newline="")

    # friend kit: program files that differ from or are added to the normal package, never game / BIOS / card
    friend = (KIT / "HOW-TO-SET-UP (FRIEND).txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    friend = friend.replace("@@PACKAGE_ID@@", kit_id).replace("\n", "\r\n")
    (DIST / "HOW-TO-SET-UP (FRIEND).txt").write_text(friend, encoding="utf-8", newline="")
    members = ["START-KH2-TEST.bat", "1-READ-ME-FIRST (KH2 TEST).txt", "PS2-ONLINE general help.txt", "package-id.txt",
               "launcher/Launcher.ps1", "link/ps2net-link.exe", "emulator/pcsx2-qtx64.exe",
               "emulator/patches/SLPM-66675_F266B00B.pnach", "emulator/patches/SLUS-21067_568A5C78.pnach",
               "MAKE-KH2-DISC/MAKE-KH2-DISC.bat", "MAKE-KH2-DISC/Make-KH2-Disc.ps1", "MAKE-KH2-DISC/" + DISC_PATCH.name]
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(DIST / "HOW-TO-SET-UP (FRIEND).txt", "HOW-TO-SET-UP (FRIEND).txt")
        for m in members:
            z.write(OUT / m, m)
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        bad = [n for n in names if n.lower().endswith((".iso", ".chd", ".cso", ".cue", ".ps2", ".rom0", ".rom1", ".nvm", ".mec", ".diff", ".bin"))
               or "/bios/" in n.lower() or "memcards" in n.lower() or "my-games" in n.lower()]
        if bad:
            sys.exit(f"friend kit contains files it must not: {bad}")
        listing = [(i.filename, i.file_size) for i in z.infolist()]
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"test package {kit_id}: {OUT} ({size / 1e6:.0f} MB, {len(files)} program files)")
    print(f"friend kit: {ZIP} ({ZIP.stat().st_size / 1e6:.1f} MB, sha1 {sha1(ZIP)})")
    for n, s_ in listing:
        print(f"  {s_:>10}  {n}")
    print("launcher sha1", sha1(OUT / "launcher" / "Launcher.ps1"), "| KH2 patch sha1", sha1(emu / "patches" / KH2_PNACH.name))


if __name__ == "__main__":
    main()
