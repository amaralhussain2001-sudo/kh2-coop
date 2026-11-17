# PS2 Online launcher. Windows PowerShell 5.1, no installation needed.
# Plays a PS2 game's own local multiplayer over the internet. Every player needs the same game file.
# Starts the connection helper (link\ps2net-link.exe) and the emulator (emulator\pcsx2-qtx64.exe) with a session file.
param([string]$Test = "")
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = Split-Path -Parent $PSScriptRoot
$EmuExe = Join-Path $Root "emulator\pcsx2-qtx64.exe"
$LinkExe = Join-Path $Root "link\ps2net-link.exe"
$GameDir = Join-Path $Root "MY-GAMES (never share)"
$LogDir = Join-Path $Root "logs"
$SettingsFile = Join-Path $Root "my-settings.txt"
$GamePort = 28150
$JoinLocalPort = 28151
New-Item -ItemType Directory -Force $LogDir | Out-Null
New-Item -ItemType Directory -Force $GameDir | Out-Null

# Controller layouts: which emulated controller slots players 1-4 use. The game decides which one works.
$Layouts = @(
    @{ Id = 3; Name = "Multitap in port 2 (Digimon Rumble Arena 2)"; Slots = "0,1,5,6"; Max = 4 },
    @{ Id = 2; Name = "Multitap in port 1 (most 3-4 player games)"; Slots = "0,2,3,4"; Max = 4 },
    @{ Id = 1; Name = "2 players, no multitap"; Slots = "0,1"; Max = 2 }
)

# Picture quality: only how THIS PC draws the picture, so every PC may choose its own (TESTS.md q01: host 8x,
# friend 1x stayed in sync). Upscale = internal resolution (1x = PS2 original, 8x = about 6K).
$Qualities = @(
    @{ Key = "auto"; Name = "Auto (best for this PC's graphics card)" },
    @{ Key = "8"; Name = "8x Ultra - RTX 4070 Ti / 5070 Ti or better"; Up = 8; Blend = 3; Aniso = 16 },
    @{ Key = "6"; Name = "6x Very high - RTX 3070 / 4060 / RX 6800"; Up = 6; Blend = 2; Aniso = 16 },
    @{ Key = "4"; Name = "4x High - GTX 1660 / RTX 2060 / RX 6600"; Up = 4; Blend = 2; Aniso = 16 },
    @{ Key = "3"; Name = "3x Medium (1080p) - GTX 1050 / RX 570"; Up = 3; Blend = 1; Aniso = 8 },
    @{ Key = "2"; Name = "2x Low - laptops, built-in graphics"; Up = 2; Blend = 1; Aniso = 4 },
    @{ Key = "1"; Name = "1x Original PS2 picture (weakest PCs)"; Up = 1; Blend = 1; Aniso = 0 }
)
$Screens = @(
    @{ Key = "16:9"; Name = "Widescreen 16:9 (if the game has a widescreen patch)" },
    @{ Key = "4:3"; Name = "Normal 4:3 (as the game was made)" }
)

function Get-Gpus {
    # Name and memory of every graphics card (Win32_VideoController reports at most 4 GB, so read the registry).
    $list = @()
    $cls = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    foreach ($k in (Get-ChildItem $cls -ErrorAction SilentlyContinue)) {
        $p = Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue
        if ($p -and $p.DriverDesc) {
            $mem = 0
            try { $mem = [double]$p.'HardwareInformation.qwMemorySize' } catch {}
            if (-not $mem) { try { $mem = [double][BitConverter]::ToUInt32($p.'HardwareInformation.MemorySize', 0) } catch {} }
            $list += [pscustomobject]@{ Name = [string]$p.DriverDesc; GB = [math]::Round($mem / 1GB, 1) }
        }
    }
    if (-not $list) { $list = @(Get-CimInstance Win32_VideoController | ForEach-Object { [pscustomobject]@{ Name = $_.Name; GB = 0 } }) }
    return $list
}

function Best-Gpu {
    $gpus = @(Get-Gpus | Where-Object { $_.Name -notmatch "Basic|Remote|Virtual|Parsec|Meta" })
    return ($gpus | Sort-Object @{ Expression = { if ($_.Name -match "NVIDIA|Radeon RX|Radeon Pro|Arc") { 1 } else { 0 } } }, GB -Descending | Select-Object -First 1)
}

function Auto-Quality($gpu) {
    if (-not $gpu) { return "2" }
    $n = $gpu.Name
    if ($n -match "RTX 50[789]0|RTX 40[89]0|RTX 4070 Ti|RX 79[05]0|RX 9070") { return "8" }
    if ($n -match "RTX 50|RTX 40|RTX 30[89]0|RTX 3070|RX 6[89]\d0|RX 7[78]00") { return "6" }
    if ($n -match "RTX 30|RTX 20|GTX 16|RX 6[67]\d0|RX 7600|RX 5[67]00|Arc.*A7[0-9]0|Arc.*B[0-9]{3}") { return "4" }
    if ($n -match "GTX 10|GTX 9|RX 5[0-9]0|RX 4[0-9]0|Arc") { return "3" }
    if ($gpu.GB -ge 6) { return "4" }
    if ($gpu.GB -ge 3) { return "3" }
    return "2" # built-in graphics (Intel UHD/Iris, AMD Radeon Graphics) or unknown
}

function Set-IniValues([string]$path, [string]$section, [hashtable]$values) {
    # Changes only the given keys of one section; keeps everything else (also repeated keys like the pad bindings).
    $lines = [System.Collections.Generic.List[string]](Get-Content $path)
    $start = -1
    for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i].Trim() -eq "[$section]") { $start = $i; break } }
    if ($start -lt 0) { $lines.Add(""); $lines.Add("[$section]"); $start = $lines.Count - 1 }
    $end = $lines.Count
    for ($i = $start + 1; $i -lt $lines.Count; $i++) { if ($lines[$i].Trim().StartsWith("[")) { $end = $i; break } }
    foreach ($key in $values.Keys) {
        $done = $false
        for ($i = $start + 1; $i -lt $end; $i++) {
            if ($lines[$i] -match ("^\s*" + [regex]::Escape($key) + "\s*=")) { $lines[$i] = "$key = $($values[$key])"; $done = $true; break }
        }
        if (-not $done) { $lines.Insert($end, "$key = $($values[$key])"); $end++ }
    }
    Set-Content -Path $path -Value $lines -Encoding UTF8
}

function Apply-Picture {
    # Writes this PC's picture settings into the emulator settings before the game starts.
    $q = $Qualities[$qualityBox.SelectedIndex]
    if ($q.Key -eq "auto") { $want = Auto-Quality $script:Gpu; $q = $Qualities | Where-Object { $_.Key -eq $want } | Select-Object -First 1 }
    $ini = Join-Path (Split-Path $EmuExe) "inis\PCSX2.ini"
    $adapter = ""
    if ($script:Gpu) { $adapter = $script:Gpu.Name }
    $gs = @{
        upscale_multiplier = $q.Up; ExtendedUpscalingMultipliers = "true"; accurate_blending_unit = $q.Blend
        MaxAnisotropy = $q.Aniso; hw_mipmap = "true"; texture_preloading = 2; dithering_ps2 = 2; OsdShowFPS = "true"
        Adapter = $adapter
    }
    Set-IniValues $ini "EmuCore/GS" $gs
    $full = "false"
    if ($fullBox.Checked) { $full = "true" }
    Set-IniValues $ini "UI" @{ StartFullscreen = $full }
    return "$($q.Up)x"
}

function Get-Games {
    $files = Get-ChildItem -Path $GameDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in @(".iso", ".chd", ".cso", ".cue") } | Sort-Object Name
    return @($files)
}

function Load-Settings {
    $s = @{ Name = $env:COMPUTERNAME; Layout = "1"; Game = ""; Quality = "auto"; Screen = "4:3"; Fullscreen = "False"; Buffer = "smooth" }
    if (Test-Path $SettingsFile) {
        foreach ($line in Get-Content $SettingsFile) { if ($line -match '^(\w+)=(.*)$') { $s[$Matches[1]] = $Matches[2] } }
    }
    return $s
}

$script:Settings = Load-Settings
function Save-Settings {
    $script:Settings.Name = $nameBox.Text
    $script:Settings.Layout = [string](Selected-Layout).Id
    if ($gameBox.SelectedItem) { $script:Settings.Game = [string]$gameBox.SelectedItem }
    $script:Settings.Quality = $Qualities[$qualityBox.SelectedIndex].Key
    $script:Settings.Screen = $Screens[$screenBox.SelectedIndex].Key
    $script:Settings.Fullscreen = [string]$fullBox.Checked
    $script:Settings.Buffer = @("smooth", "fast")[$bufferBox.SelectedIndex]
    $lines = @(); foreach ($k in $script:Settings.Keys) { $lines += "$k=$($script:Settings[$k])" }
    Set-Content -Path $SettingsFile -Value $lines -Encoding UTF8
}

$script:Helper = $null
$script:Emu = $null
$script:HelperLog = $null
$script:HelperLogPos = 0
$script:Mode = ""
$script:PendingJoin = $false

# ---------------------------------------------------------------------------------------------------------------
# Window
$form = New-Object System.Windows.Forms.Form
$form.Text = "PS2 Online - KH2 two-player TEST"
$form.Size = New-Object System.Drawing.Size(640, 812)
$form.StartPosition = "CenterScreen"
$form.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

function Add-Label($text, $x, $y, $w = 600, $h = 22, $bold = $false) {
    $l = New-Object System.Windows.Forms.Label
    $l.Text = $text; $l.Location = New-Object System.Drawing.Point($x, $y); $l.Size = New-Object System.Drawing.Size($w, $h)
    if ($bold) { $l.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold); $l.Tag = "heading" }
    $form.Controls.Add($l); return $l
}
function Add-Button($text, $x, $y, $w = 150, $h = 30) {
    $b = New-Object System.Windows.Forms.Button
    $b.Text = $text; $b.Location = New-Object System.Drawing.Point($x, $y); $b.Size = New-Object System.Drawing.Size($w, $h)
    $form.Controls.Add($b); return $b
}
function Add-Box($x, $y, $w, $h = 26, $multi = $false) {
    $t = New-Object System.Windows.Forms.TextBox
    $t.Location = New-Object System.Drawing.Point($x, $y); $t.Size = New-Object System.Drawing.Size($w, $h)
    if ($multi) { $t.Multiline = $true; $t.ScrollBars = "Vertical" }
    $form.Controls.Add($t); return $t
}
function Add-Combo($x, $y, $w) {
    $c = New-Object System.Windows.Forms.ComboBox
    $c.Location = New-Object System.Drawing.Point($x, $y); $c.Size = New-Object System.Drawing.Size($w, 26)
    $c.DropDownStyle = "DropDownList"; $form.Controls.Add($c); return $c
}

Add-Label "Your name:" 16 14 90 | Out-Null
$nameBox = Add-Box 110 12 200
$nameBox.Text = $script:Settings.Name
$nameBox.MaxLength = 15

Add-Label "Game:" 16 50 90 | Out-Null
$gameBox = Add-Combo 110 47 400
$refreshButton = Add-Button "Refresh" 516 46 90 28
Add-Label "Controllers:" 16 84 90 | Out-Null
$layoutBox = Add-Combo 110 81 400
foreach ($l in $Layouts) { [void]$layoutBox.Items.Add($l.Name) }
$idx = 0; for ($i = 0; $i -lt $Layouts.Count; $i++) { if ([string]$Layouts[$i].Id -eq $script:Settings.Layout) { $idx = $i } }
$layoutBox.SelectedIndex = $idx
Add-Label "Screen:" 16 116 90 | Out-Null
$screenBox = Add-Combo 110 113 400
foreach ($s in $Screens) { [void]$screenBox.Items.Add($s.Name) }
$screenBox.SelectedIndex = [Math]::Max(0, [array]::IndexOf(@($Screens | ForEach-Object { $_.Key }), $script:Settings.Screen))
Add-Label "(Game, controllers and screen of the HOST are sent to friends inside the join code.)" 110 140 510 20 | Out-Null
Add-Label "Picture:" 16 166 90 | Out-Null
$qualityBox = Add-Combo 110 163 400
foreach ($q in $Qualities) { [void]$qualityBox.Items.Add($q.Name) }
$qualityBox.SelectedIndex = [Math]::Max(0, [array]::IndexOf(@($Qualities | ForEach-Object { $_.Key }), $script:Settings.Quality))
$fullBox = New-Object System.Windows.Forms.CheckBox
$fullBox.Text = "Full screen"; $fullBox.Location = New-Object System.Drawing.Point(516, 164); $fullBox.Size = New-Object System.Drawing.Size(110, 24)
$fullBox.Checked = ($script:Settings.Fullscreen -eq "True"); $form.Controls.Add($fullBox)
$gpuLabel = Add-Label "" 110 190 510 20

Add-Label "1) HOST A GAME (you are player 1)" 16 228 600 22 $true | Out-Null
Add-Label "Players:" 16 260 60 | Out-Null
Add-Label "Connection:" 330 260 80 | Out-Null
$bufferBox = Add-Combo 412 257 194
[void]$bufferBox.Items.Add("Smooth (fewer pauses)"); [void]$bufferBox.Items.Add("Fast (quickest buttons)")
if ($script:Settings.Buffer -eq "fast") { $bufferBox.SelectedIndex = 1 } else { $bufferBox.SelectedIndex = 0 }
$playersBox = Add-Combo 80 257 50
$hostButton = Add-Button "Host a game" 150 255 160

Add-Label "2) JOIN A GAME: paste the host's join code (PSN1-...)" 16 300 600 22 $true | Out-Null
$joinBox = Add-Box 16 326 470
$joinButton = Add-Button "Join" 496 324 110

Add-Label "3) SAME HOUSE: join by the host's IP address (choose the same game and controllers above)" 16 366 610 22 $true | Out-Null
$ipBox = Add-Box 16 392 200
$ipButton = Add-Button "Join by IP" 226 390 120

$padButton = Add-Button "Controller settings" 16 432 180
$stopButton = Add-Button "Stop" 206 432 100
$stopButton.Enabled = $false

Add-Label "Code to send (already copied to the clipboard):" 16 474 600 | Out-Null
$codeBox = Add-Box 16 498 470
$codeBox.ReadOnly = $true
$copyButton = Add-Button "Copy again" 496 496 110

Add-Label "Host only: paste a friend's reply code (PSR1-...) if the friend is not connected:" 16 534 600 | Out-Null
$replyBox = Add-Box 16 558 470
$replyButton = Add-Button "Add reply" 496 556 110

Add-Label "What is happening:" 16 594 600 | Out-Null
$statusBox = Add-Box 16 618 590 140 $true
$statusBox.ReadOnly = $true

function Say([string]$text) {
    $line = (Get-Date -Format "HH:mm:ss") + "  " + $text
    $statusBox.AppendText($line + "`r`n")
    # TEST PACKAGE: also keep what this window said in the logs folder, so the logs tell the whole story
    try { Add-Content -LiteralPath (Join-Path $LogDir ((Get-Date -Format "yyyy-MM-dd") + "-launcher.txt")) -Value $line -Encoding UTF8 } catch {}
}

function Selected-Layout { return $Layouts[$layoutBox.SelectedIndex] }

function Fill-Players {
    $max = (Selected-Layout).Max
    $playersBox.Items.Clear()
    for ($n = 2; $n -le $max; $n++) { [void]$playersBox.Items.Add([string]$n) }
    $playersBox.SelectedIndex = 0
}

function Fill-Games {
    $gameBox.Items.Clear()
    foreach ($g in Get-Games) { [void]$gameBox.Items.Add($g.Name) }
    if ($gameBox.Items.Count -gt 0) {
        $i = $gameBox.Items.IndexOf($script:Settings.Game)
        $gameBox.SelectedIndex = [Math]::Max($i, 0)
    }
}

function Selected-GamePath {
    if (-not $gameBox.SelectedItem) { return $null }
    return (Join-Path $GameDir ([string]$gameBox.SelectedItem))
}

$layoutBox.Add_SelectedIndexChanged({ Fill-Players })
$refreshButton.Add_Click({ Fill-Games; Say "Game list refreshed ($($gameBox.Items.Count) found)." })
Fill-Players
Fill-Games
# A helper left over from an earlier launcher (closed in an unusual way) would block the UDP port: stop it.
try {
    Get-CimInstance Win32_Process -Filter "Name='ps2net-link.exe'" -ErrorAction Stop |
        Where-Object { $_.ExecutablePath -eq $LinkExe } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
} catch {}
$script:Gpu = Best-Gpu
# This is a modified PCSX2: an official update would replace it and switch the online mode off.
try { Set-IniValues (Join-Path (Split-Path $EmuExe) "inis\PCSX2.ini") "AutoUpdater" @{ CheckAtStartup = "false" } } catch {}
$autoQ = Auto-Quality $script:Gpu
if ($script:Gpu) { $gpuLabel.Text = "Graphics card: $($script:Gpu.Name) ($($script:Gpu.GB) GB) - Auto picks ${autoQ}x" }
else { $gpuLabel.Text = "Graphics card not found - Auto picks 2x" }

function Set-Busy([bool]$busy) {
    foreach ($c in @($hostButton, $joinButton, $ipButton, $padButton, $gameBox, $layoutBox, $playersBox, $refreshButton, $screenBox, $qualityBox, $fullBox, $bufferBox)) { $c.Enabled = -not $busy }
    $stopButton.Enabled = $busy
}

function Show-Code([string]$code) {
    $codeBox.Text = $code
    try { Set-Clipboard -Value $code } catch {}
}

# The join code carries a tag: 1 byte layout id + 6 bytes game file size, so friends start the same game and layout.
# TEST PACKAGE: the game file's check number (SHA-1), remembered per file so it is computed once.
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
function Make-Tag([int]$layoutId, [int]$flags, [long]$size, [string]$check) { return ("{0:X2}{1:X2}{2:X12}{3}" -f $layoutId, $flags, $size, $check.Substring(0, 16).ToUpper()) }
function Screen-Flag { if ($Screens[$screenBox.SelectedIndex].Key -eq "16:9") { return 1 } else { return 0 } }

# ---------------------------------------------------------------------------------------------------------------
# Processes
function Start-Helper([string[]]$argsList) {
    $stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $script:HelperLog = Join-Path $LogDir "$stamp-connection.txt"
    $script:HelperLogPos = 0
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $LinkExe
    $psi.Arguments = (($argsList + @("--log", "`"$($script:HelperLog)`"")) -join " ")
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true # the launcher reads the log file; the pipe is only drained
    $script:Helper = [System.Diagnostics.Process]::Start($psi)
    $script:Helper.BeginOutputReadLine()
}

function Start-Emulator([string]$gamePath, [hashtable]$session) {
    if (-not $gamePath -or -not (Test-Path $gamePath)) { Say "No game file. Put your game (.iso, .chd, .cso or .cue) into the folder 'MY-GAMES (never share)' and press Refresh."; return $false }
    $check = Game-Check $gamePath
    Write-CheckFile $check
    $picture = Apply-Picture
    $stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $ini = Join-Path $LogDir "session.ini"
    $lines = @()
    foreach ($k in $session.Keys) { $lines += "$k = $($session[$k])" }
    $lines += "LogFile = $(Join-Path $LogDir "$stamp-game.txt")"
    if ($Test -and $env:PS2ONLINE_TEST_EXTRA -and (Test-Path -LiteralPath $env:PS2ONLINE_TEST_EXTRA)) { $lines += Get-Content -LiteralPath $env:PS2ONLINE_TEST_EXTRA } # test only (rehearsal bots)
    Set-Content -Path $ini -Value $lines -Encoding ASCII
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $EmuExe
    $psi.Arguments = "-batch -fastboot -- `"$gamePath`""
    $psi.WorkingDirectory = Split-Path $EmuExe
    $psi.UseShellExecute = $false
    $psi.EnvironmentVariables["PS2NET_CONFIG"] = $ini
    $script:Emu = [System.Diagnostics.Process]::Start($psi)
    Say "Game: $(Split-Path $gamePath -Leaf). Controllers: $($session.LayoutName). Screen: $($session.Screen). Picture: $picture."
    Say "Game file check: $(Show-Check $check)  (must be the same on every player's PC)"
    return $true
}

function Stop-All {
    if ($script:Helper -and -not $script:Helper.HasExited) {
        try { $script:Helper.StandardInput.WriteLine("quit"); $script:Helper.WaitForExit(1500) | Out-Null } catch {}
        if (-not $script:Helper.HasExited) { $script:Helper.Kill() }
    }
    if ($script:Emu -and -not $script:Emu.HasExited) { $script:Emu.CloseMainWindow() | Out-Null }
    $script:Helper = $null; $script:Emu = $null; $script:Mode = ""; $script:PendingJoin = $false
    Set-Busy $false
}

function Start-JoinedGame([string]$tagHex) {
    # Friend side: pick the game file and layout the host chose (from the join code).
    $script:PendingJoin = $false
    if ($tagHex -notmatch '^[0-9A-F]{32}$') { Say "This join code is from another package. Everyone needs this same KH2 TEST folder (see package-id.txt)."; Stop-All; return }
    $layoutId = [Convert]::ToInt32($tagHex.Substring(0, 2), 16)
    $flags = [Convert]::ToInt32($tagHex.Substring(2, 2), 16)
    $size = [Convert]::ToInt64($tagHex.Substring(4, 12), 16)
    $hostCheck = $tagHex.Substring(16, 16)
    $layout = $Layouts | Where-Object { $_.Id -eq $layoutId } | Select-Object -First 1
    if (-not $layout) { Say "Unknown controller layout in the join code. Everyone needs the same package version."; Stop-All; return }
    $game = $null
    $sameSize = @(Get-Games | Where-Object { $_.Length -eq $size })
    foreach ($g in $sameSize) { if ((Game-Check $g.FullName).Substring(0, 16).ToUpper() -eq $hostCheck) { $game = $g; break } }
    if (-not $game -and $sameSize.Count -gt 0) {
        Say "Your game file has the right size but NOT the same content as the host's (host: $(Show-Check $hostCheck), yours: $(Show-Check (Game-Check $sameSize[0].FullName))). For Kingdom Hearts II both players must make the disc file with MAKE-KH2-DISC and get the same check number."
        Stop-All; return
    }
    if (-not $game) {
        Say "You do not have the host's game (its file is $size bytes). Put the SAME game file into 'MY-GAMES (never share)', press Refresh and join again."
        Stop-All; return
    }
    $gameBox.SelectedItem = $game.Name
    $layoutBox.SelectedIndex = [array]::IndexOf(($Layouts | ForEach-Object { $_.Id }), $layoutId)
    if ($flags -band 1) { $screenBox.SelectedIndex = 0 } else { $screenBox.SelectedIndex = 1 }
    Save-Settings
    $ok = Start-Emulator $game.FullName @{ Role = "client"; Host = "127.0.0.1"; Port = $JoinLocalPort; Name = $nameBox.Text; Slots = $layout.Slots; LayoutName = $layout.Name; Screen = $Screens[$screenBox.SelectedIndex].Key }
    if (-not $ok) { Stop-All }
}

function Handle-HelperLine([string]$line) {
    if (-not $script:Helper) { return } # TEST PACKAGE: nothing is running any more (for example after a refused join)
    $msg = $line -replace '^\d+ ', ''
    if ($msg -match '^@code join (\S+)') {
        Show-Code $Matches[1]
        Say "Your JOIN CODE is ready and copied. Paste it to your friends (WhatsApp, Discord, ...)."
    } elseif ($msg -match '^@tag (\S+)') {
        if ($script:PendingJoin) { Start-JoinedGame $Matches[1] }
    } elseif ($msg -match '^@code reply (\S+)') {
        Show-Code $Matches[1]
        Say "Connecting to the host... If it does not say 'Connected' within 10 seconds, send the code above to the host."
    } elseif ($msg -match '^@connected') { Say "Connected to the host." }
    elseif ($msg -match '^@joined (\d+)') { Say "A friend connected (connection $($Matches[1]))." }
    elseif ($msg -match '^@lost') { Say "A connection was lost; trying again..." }
    elseif ($msg -match '^@bad_code (.*)') { Say $Matches[1]; if ($script:Mode -eq "join") { Stop-All } }
    elseif ($msg -match '^@warning (.*)') { Say ("Warning: " + $Matches[1]) }
    elseif ($msg -match '^@error (.*)') { Say ("Problem: " + $Matches[1]) }
    elseif ($msg -match '^@gave_up') { Say "Could not reach the host for 10 minutes. See 1-READ-ME-FIRST.txt, part 'If it does not connect'." }
    elseif ($msg -match '^@full') { Say "Someone else tried to join, but the game is full." }
}

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 300
$timer.Add_Tick({
    if ($script:HelperLog -and (Test-Path $script:HelperLog)) {
        try {
            $fs = [System.IO.File]::Open($script:HelperLog, 'Open', 'Read', 'ReadWrite')
            $fs.Seek($script:HelperLogPos, 'Begin') | Out-Null
            $sr = New-Object System.IO.StreamReader($fs)
            $text = $sr.ReadToEnd()
            $script:HelperLogPos = $fs.Position
            $sr.Close()
            foreach ($l in ($text -split "`n")) { if ($l.Trim()) { Handle-HelperLine $l.Trim() } }
        } catch {}
    }
    if ($script:Mode -ne "" -and $script:Emu -and $script:Emu.HasExited) {
        Say "The game was closed."
        Stop-All
    }
})
$timer.Start()

# ---------------------------------------------------------------------------------------------------------------
# Buttons
$hostButton.Add_Click({
    Save-Settings
    $game = Selected-GamePath
    if (-not $game) { Say "Choose a game first (put it into 'MY-GAMES (never share)' and press Refresh)."; return }
    $layout = Selected-Layout
    $players = [int]$playersBox.SelectedItem
    $tag = Make-Tag $layout.Id (Screen-Flag) (Get-Item -LiteralPath $game).Length (Game-Check $game)
    Set-Busy $true; $codeBox.Text = ""; $script:Mode = "host"
    Say "Hosting $players players. Getting your join code..."
    Start-Helper @("host", "--players", $players, "--emu-port", $GamePort, "--tag", $tag)
    $ok = Start-Emulator $game @{ Role = "host"; Port = $GamePort; Players = $players; Name = $nameBox.Text; Slots = $layout.Slots; LayoutName = $layout.Name; Screen = $Screens[$screenBox.SelectedIndex].Key; Buffer = @("smooth", "fast")[$bufferBox.SelectedIndex] }
    if (-not $ok) { Stop-All; return }
    Say "The game window waits until everybody is connected. In most games every player presses START on the title screen."
})

$joinButton.Add_Click({
    Save-Settings
    $code = $joinBox.Text
    if ($code -notmatch 'PSN1-') { Say "Paste the host's join code (it starts with PSN1-) into the box first."; return }
    $clean = ($code -replace '[\r\n\s"]', '')
    Set-Busy $true; $codeBox.Text = ""; $script:Mode = "join"; $script:PendingJoin = $true
    Say "Joining... (reading the host's game and controllers from the code)"
    Start-Helper @("join", "`"$clean`"", "--listen-port", $JoinLocalPort)
})

$ipButton.Add_Click({
    Save-Settings
    $ip = $ipBox.Text.Trim()
    if (-not $ip) { Say "Type the host's IP address first (on the host PC: cmd > ipconfig > IPv4 Address)."; return }
    $layout = Selected-Layout
    Set-Busy $true; $codeBox.Text = ""; $script:Mode = "ip"
    Say "Joining $ip directly (same house)..."
    $ok = Start-Emulator (Selected-GamePath) @{ Role = "client"; Host = $ip; Port = $GamePort; Name = $nameBox.Text; Slots = $layout.Slots; LayoutName = $layout.Name; Screen = $Screens[$screenBox.SelectedIndex].Key }
    if (-not $ok) { Stop-All; return }
})

$replyButton.Add_Click({
    if ($script:Mode -ne "host" -or -not $script:Helper) { Say "Reply codes are only for the host, while hosting."; return }
    $code = ($replyBox.Text -replace '[\r\n"]', ' ')
    if ($code -notmatch 'PSR1-') { Say "Paste the friend's reply code (it starts with PSR1-)."; return }
    $script:Helper.StandardInput.WriteLine($code)
    $replyBox.Text = ""
    Say "Reply code added. Connecting to that friend..."
})

$padButton.Add_Click({
    # Normal emulator window without a game and without online mode, to set up keyboard/gamepad (Settings > Controllers).
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $EmuExe; $psi.WorkingDirectory = Split-Path $EmuExe; $psi.UseShellExecute = $false
    [System.Diagnostics.Process]::Start($psi) | Out-Null
    Say "In the emulator: Settings > Controllers > Controller Port 1. Change only the controls. Close it when done."
})

$copyButton.Add_Click({ if ($codeBox.Text) { Set-Clipboard -Value $codeBox.Text; Say "Copied." } })
$stopButton.Add_Click({ Say "Stopping."; Stop-All })
$form.Add_FormClosing({ Stop-All })

# ---------------------------------------------------------------------------------------------------------------
# Dark mode
function Apply-DarkTheme {
    $bg = [System.Drawing.Color]::FromArgb(30, 30, 32)       # window
    $panel = [System.Drawing.Color]::FromArgb(45, 45, 48)    # boxes
    $button = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $border = [System.Drawing.Color]::FromArgb(90, 90, 96)
    $text = [System.Drawing.Color]::FromArgb(230, 230, 230)
    $dim = [System.Drawing.Color]::FromArgb(160, 160, 165)
    $accent = [System.Drawing.Color]::FromArgb(110, 190, 255) # headings
    $form.BackColor = $bg; $form.ForeColor = $text
    foreach ($c in $form.Controls) {
        if ($c -is [System.Windows.Forms.Button]) {
            $c.FlatStyle = "Flat"; $c.BackColor = $button; $c.ForeColor = $text
            $c.FlatAppearance.BorderColor = $border
            $c.FlatAppearance.MouseOverBackColor = [System.Drawing.Color]::FromArgb(80, 80, 86)
            $c.FlatAppearance.MouseDownBackColor = [System.Drawing.Color]::FromArgb(0, 102, 180)
        } elseif ($c -is [System.Windows.Forms.TextBox]) {
            $c.BackColor = $panel; $c.ForeColor = $text; $c.BorderStyle = "FixedSingle"
        } elseif ($c -is [System.Windows.Forms.ComboBox]) {
            $c.FlatStyle = "Flat"; $c.BackColor = $panel; $c.ForeColor = $text
        } elseif ($c -is [System.Windows.Forms.CheckBox]) {
            $c.ForeColor = $text; $c.BackColor = $bg
        } elseif ($c -is [System.Windows.Forms.Label]) {
            $c.BackColor = $bg
            if ($c.Tag -eq "heading") { $c.ForeColor = $accent } elseif ($c.Text.StartsWith("(") -or $c -eq $gpuLabel) { $c.ForeColor = $dim } else { $c.ForeColor = $text }
        }
    }
    # dark title bar (Windows 10 1809+ / 11); ignored on older Windows
    try {
        Add-Type -Namespace W -Name Dwm -MemberDefinition '[DllImport("dwmapi.dll")] public static extern int DwmSetWindowAttribute(System.IntPtr hwnd, int attr, ref int value, int size);' -ErrorAction Stop
        $form.Add_HandleCreated({ $on = 1; [void][W.Dwm]::DwmSetWindowAttribute($form.Handle, 20, [ref]$on, 4) })
    } catch {}
}
Apply-DarkTheme

if (-not (Test-Path $EmuExe) -or -not (Test-Path $LinkExe)) {
    [System.Windows.Forms.MessageBox]::Show("Some program files are missing. Copy the whole PS2-ONLINE folder again.", "PS2 Online") | Out-Null
}
if ($gameBox.Items.Count -eq 0) { Say "Put your game file (.iso, .chd, .cso or .cue) into 'MY-GAMES (never share)', then press Refresh." }
else { Say "Ready. Host a game, or paste a join code and press Join." }
if ($Test -eq "parse") { "launcher parsed OK"; exit 0 }
if ($Test -eq "tiers") {
    # test only: what Auto picks for typical graphics cards
    foreach ($g in @(
        @("NVIDIA GeForce RTX 5090", 32), @("NVIDIA GeForce RTX 5070 Ti", 16), @("NVIDIA GeForce RTX 4060", 8),
        @("NVIDIA GeForce RTX 3060", 12), @("NVIDIA GeForce GTX 1660 SUPER", 6), @("NVIDIA GeForce GTX 1050 Ti", 4),
        @("AMD Radeon RX 7900 XTX", 24), @("AMD Radeon RX 6600", 8), @("AMD Radeon RX 580", 8),
        @("Intel(R) Arc(TM) A750 Graphics", 8), @("Intel(R) UHD Graphics 620", 1), @("AMD Radeon(TM) Graphics", 2))) {
        "{0,-32} {1,3} GB -> {2}x" -f $g[0], $g[1], (Auto-Quality ([pscustomobject]@{ Name = $g[0]; GB = $g[1] }))
    }
    exit 0
}
if ($Test -like "shot:*") {
    # test only: save a picture of the window, then close
    $form.Add_Shown({
        $bmp = New-Object System.Drawing.Bitmap($form.Width, $form.Height)
        $form.DrawToBitmap($bmp, (New-Object System.Drawing.Rectangle(0, 0, $form.Width, $form.Height)))
        $bmp.Save($Test.Substring(5)); $bmp.Dispose(); $form.Close()
    })
}
if ($Test -eq "host") { $form.Add_Shown({ $hostButton.PerformClick() }) } # test only
if ($Test -like "join:*") { $form.Add_Shown({ $joinBox.Text = $Test.Substring(5); $joinButton.PerformClick() }) } # test only
if ($Test -like "ip:*") { $form.Add_Shown({ $ipBox.Text = $Test.Substring(3); $ipButton.PerformClick() }) } # test only
[void]$form.ShowDialog()
