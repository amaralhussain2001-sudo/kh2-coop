"""One-off: the test package goes to BUILD 28 = build 27 + the eightieth glue --difficulty (docs/STATE.md part 143: the host chooses
how strong ordinary enemies are). patches/merged-v20 = merge_v7.py with build 27's options + --difficulty, merged-v20-own =
make_own.py --base merged-v20 --cannon2view. The disc file and the emulator (builds/card1) do not change.
Edits:
  - make_package_patch.py: v19 -> v20; both shipped patch files get the difficulty line (patch=1,EE,000DE810,word,0) in front of the
    widescreen group, which the launcher sets before every start;
  - make_test_package.py: v19 -> v20; its "starts with exactly the merged lines" check leaves the difficulty line out; the launcher
    gets an "Enemies:" box (host), the value travels in the join code's flags byte (bits 1-2; bit 0 is the screen), and
    Write-Difficulty sets the line in emulator\\patches\\SLPM-66675_F266B00B.pnach before the emulator starts;
  - the kit's read-me (NEW IN BUILD 28) and two-PC start text (13 TO 28).
  python -I tools/package/edit_package_v28.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"

NEW28 = """NEW IN BUILD 28 (the disc file and the emulator are the same as in build 27), one change in the patch file and the launcher:
(1) HOW STRONG ARE ORDINARY ENEMIES? THE HOST CHOOSES: in the launcher, under "1) HOST A GAME", the box "Enemies:":
      Normal              as before (the original game's enemies; bosses +75 % HP as since build 1)
      Hard (+50% HP)      ordinary enemies have half as much HP again
      Very hard (x2 HP)   ordinary enemies have double HP
    Bosses keep their +75 % in every choice. The host's choice travels in the join code, so the friend's PC uses the same by
    itself (the friend's own box is set to it). Joining by IP: both must choose the same, or the join is refused ("Different
    patch files"). Only with two heroes; a game with one hero is never changed.
    Tested on one PC: two fights at each choice: ordinary enemies 10 -> 15 -> 20 HP, the bosses of those fights 280 and 420 in
    all three, never out of sync.
"""

ADD_EDITS = r'''
EDITS += [
    # BUILD 28 (edit_package_v28.py): the co-op difficulty (glue 80). Settings, the box, Set-Busy, the join code, the patch line.
    ('Fullscreen = "False"; Buffer = "smooth" }', 'Fullscreen = "False"; Buffer = "smooth"; Difficulty = "0" }'),
    ('    $script:Settings.Buffer = @("smooth", "fast")[$bufferBox.SelectedIndex]\n',
     '    $script:Settings.Buffer = @("smooth", "fast")[$bufferBox.SelectedIndex]\n'
     '    $script:Settings.Difficulty = [string]$diffBox.SelectedIndex\n'),
    ('if ($script:Settings.Buffer -eq "fast") { $bufferBox.SelectedIndex = 1 } else { $bufferBox.SelectedIndex = 0 }\n',
     'if ($script:Settings.Buffer -eq "fast") { $bufferBox.SelectedIndex = 1 } else { $bufferBox.SelectedIndex = 0 }\n'
     '# TEST PACKAGE (build 28): how strong ordinary enemies are; the host\'s choice travels in the join code\n'
     'Add-Label "Enemies:" 140 260 60 | Out-Null\n'
     '$diffBox = Add-Combo 200 257 124\n'
     '[void]$diffBox.Items.Add("Normal"); [void]$diffBox.Items.Add("Hard (+50% HP)"); [void]$diffBox.Items.Add("Very hard (x2 HP)")\n'
     '$diffSet = 0; [void][int]::TryParse([string]$script:Settings.Difficulty, [ref]$diffSet); $diffBox.SelectedIndex = [Math]::Max(0, [Math]::Min(2, $diffSet))\n'),
    ('$screenBox, $qualityBox, $fullBox, $bufferBox)) { $c.Enabled = -not $busy }',
     '$screenBox, $qualityBox, $fullBox, $bufferBox, $diffBox)) { $c.Enabled = -not $busy }'),
    ('    $tag = Make-Tag $layout.Id (Screen-Flag) (Get-Item -LiteralPath $game).Length (Game-Check $game)\n',
     '    $tag = Make-Tag $layout.Id ((Screen-Flag) -bor ($diffBox.SelectedIndex -shl 1)) (Get-Item -LiteralPath $game).Length (Game-Check $game)\n'),
    ('    if ($flags -band 1) { $screenBox.SelectedIndex = 0 } else { $screenBox.SelectedIndex = 1 }\n',
     '    if ($flags -band 1) { $screenBox.SelectedIndex = 0 } else { $screenBox.SelectedIndex = 1 }\n'
     '    $diffBox.SelectedIndex = [Math]::Min(2, (($flags -shr 1) -band 3))   # TEST PACKAGE (build 28): the host\'s enemies\n'),
    ('    Write-CheckFile $check\n',
     '    Write-CheckFile $check\n'
     '    Write-Difficulty $diffBox.SelectedIndex\n'),
    ('function Show-Check([string]$hash) {\n',
     '# TEST PACKAGE (build 28): the co-op difficulty word of the KH2 patch (glue 80): 0 normal, 1 hard, 2 very hard. The line is in the\n'
     '# shipped patch file; the launcher only sets its value. The patch files are compared at the join, so both PCs must agree.\n'
     'function Write-Difficulty([int]$d) {\n'
     '    $file = Join-Path (Split-Path $EmuExe) "patches\\SLPM-66675_F266B00B.pnach"\n'
     '    if (-not (Test-Path -LiteralPath $file)) { return }\n'
     '    $text = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::ASCII)\n'
     '    $line = "patch=1,EE,000DE810,word,{0:X8}" -f $d\n'
     '    $new = [regex]::Replace($text, "(?m)^patch=1,EE,000DE810,word,[0-9A-Fa-f]{8}", $line)\n'
     '    if ($new -ne $text) { [System.IO.File]::WriteAllText($file, $new, [System.Text.Encoding]::ASCII) }\n'
     '    if ($text -match "(?m)^patch=1,EE,000DE810,word,") { Say ("Enemies: " + @("Normal", "Hard (+50% HP)", "Very hard (x2 HP)")[$d] + " (bosses +75 % HP in every choice).") }\n'
     '}\n'
     'function Show-Check([string]$hash) {\n'),
]
'''


def edit(path, pairs):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8-sig").replace("\r\n", "\n")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) >= 1:      # this pair is already in (a first run stopped half way)
            continue
        assert t.count(old) == 1, (str(path), t.count(old), old[:70])
        t = t.replace(old, new)
    out = t.replace("\n", "\r\n") if crlf else t
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    print("edited", path)


if "TEST BUILD 28" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 28")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v20", "merged-v20-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v19-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v20-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v19) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v20) + the same group"),
    ('make("patches/merged-v19-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v20-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v19-own, tools/own/make_own.py --base merged-v19 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v20-own, tools/own/make_own.py --base merged-v20 --cannon2view)")'),
    ('make("patches/merged-v19/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v20/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
    ('    d.write_text("\\n".join(head + lines) + "\\n\\n" + tail, encoding="ascii", newline="\\n")',
     '    diff = ["comment=Co-op difficulty (glue 80, build 28): the LAUNCHER sets the next line from the host\'s choice "\n'
     '            "(0 normal, 1 hard: ordinary enemies x 1.5 HP, 2 very hard: x 2). Both PCs must have the same value.",\n'
     '            "patch=1,EE,000DE810,word,00000000"]\n'
     '    d.write_text("\\n".join(head + lines + diff) + "\\n\\n" + tail, encoding="ascii", newline="\\n")'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v19-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v20-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v19" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v20" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v19-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v20-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v19 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v20 lines")'),
    ('    ours = [l.strip() for l in head.splitlines() if l.startswith("patch=")]\n',
     '    ours = [l.strip() for l in head.splitlines() if l.startswith("patch=") and not l.startswith("patch=1,EE,000DE810,")]  # (build 28: the launcher\'s difficulty line)\n'),
    ('    if [l.strip() for l in head2.splitlines() if l.startswith("patch=")] != patch_lines(SHARED):\n',
     '    if [l.strip() for l in head2.splitlines() if l.startswith("patch=") and not l.startswith("patch=1,EE,000DE810,")] != patch_lines(SHARED):\n'),
    ("\n\ndef patch_launcher(text):", ADD_EDITS + "\n\ndef patch_launcher(text):"),
])
edit(START, [
    ("   BUILDS 13 TO 27 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 28 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 27 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 28 (OWN SCREENS)"),
    ("NEW IN BUILD 27 (the disc file and the emulator are the same as in build 26), one change in the patch file:\n",
     NEW28 + "NEW IN BUILD 27 (the disc file and the emulator are the same as in build 26), one change in the patch file:\n"),
])
