# Makes the Kingdom Hearts II two-player TEST disc file from YOUR OWN original disc file.
# Windows PowerShell 5.1, nothing to install. Your original file is only read; a NEW file is written.
#   Double-click MAKE-KH2-DISC.bat (a window asks for your original file), or drag your original file onto the .bat.
param(
    [string]$Original = "",
    [string]$OutFile = "",     # test use: write somewhere else
    [switch]$NoPause           # test use: do not wait for Enter at the end
)
$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$PatchFile = Join-Path $Here "kh2-coop-v5.kh2patch"
$PatchSha1 = "@@PATCH_SHA1@@"
$OutName = "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso"
$Root = Split-Path -Parent $Here
$OutDir = Join-Path $Root "MY-GAMES (never share)"

function Finish([int]$code) {
    if (-not $NoPause) { Write-Host ""; Read-Host "Press Enter to close this window" | Out-Null }
    exit $code
}
function Fail([string]$text) {
    Write-Host ""
    Write-Host "NOT DONE: $text" -ForegroundColor Red
    Finish 1
}
function Hex([byte[]]$bytes) { return ([BitConverter]::ToString($bytes).Replace("-", "").ToLower()) }
function FileSha1([string]$path) { return (Get-FileHash -Algorithm SHA1 -LiteralPath $path).Hash.ToLower() }

Write-Host "Kingdom Hearts II two-player TEST disc maker"
Write-Host "============================================"
Write-Host "It reads your own original disc file and writes a NEW file. Your original is not changed."
Write-Host ""

try {
    if (-not (Test-Path -LiteralPath $PatchFile)) { Fail "The file kh2-coop-v5.kh2patch is missing next to this script. Unzip the whole folder again." }
    Write-Host "Step 1 of 5: checking the patch file..."
    $got = FileSha1 $PatchFile
    if ($got -ne $PatchSha1) { Fail "The patch file is damaged (its check number is $got, expected $PatchSha1). Unzip or download the folder again." }

    if (-not $Original) {
        Add-Type -AssemblyName System.Windows.Forms
        $dlg = New-Object System.Windows.Forms.OpenFileDialog
        $dlg.Title = "Choose YOUR original disc file: Kingdom Hearts II - Final Mix (Japan).iso"
        $dlg.Filter = "PS2 disc image (*.iso)|*.iso|All files (*.*)|*.*"
        if ($dlg.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { Fail "No file was chosen." }
        $Original = $dlg.FileName
    }
    if (-not (Test-Path -LiteralPath $Original)) { Fail "File not found: $Original" }
    $Original = (Get-Item -LiteralPath $Original).FullName

    $ps = [System.IO.File]::OpenRead($PatchFile)
    $pr = New-Object System.IO.BinaryReader($ps)
    $magic = [System.Text.Encoding]::ASCII.GetString($pr.ReadBytes(8))
    if ($magic -ne "KH2SECT1") { $pr.Close(); Fail "The patch file has an unknown format." }
    $sector = [int64]$pr.ReadUInt32()
    $srcSize = [int64]$pr.ReadUInt64()
    $srcSha = Hex ($pr.ReadBytes(20))
    $dstSize = [int64]$pr.ReadUInt64()
    $dstSha = Hex ($pr.ReadBytes(20))
    $runs = [int]$pr.ReadUInt32()

    $len = (Get-Item -LiteralPath $Original).Length
    if ($len -ne $srcSize) {
        $pr.Close()
        Fail "This is not the expected disc file: it is $len bytes, the original 'Kingdom Hearts II - Final Mix (Japan)' disc file is $srcSize bytes."
    }
    Write-Host "Step 2 of 5: checking your original disc file (about a minute)..."
    $got = FileSha1 $Original
    if ($got -ne $srcSha) {
        $pr.Close()
        Fail "This is not the expected disc file. Its check number (SHA-1) is $got, expected $srcSha. It must be the unmodified 'Kingdom Hearts II - Final Mix (Japan)' disc (SLPM-66675)."
    }

    if (-not $OutFile) {
        New-Item -ItemType Directory -Force $OutDir | Out-Null
        $OutFile = Join-Path $OutDir $OutName
    }
    $OutFile = [System.IO.Path]::GetFullPath($OutFile)
    if ($OutFile -ieq $Original) { $pr.Close(); Fail "The new file would have the same name and folder as your original. Keep your original somewhere else." }
    $drive = New-Object System.IO.DriveInfo(([System.IO.Path]::GetPathRoot($OutFile)))
    $need = $dstSize + 100MB
    if ((Test-Path -LiteralPath $OutFile)) { $need = $need - (Get-Item -LiteralPath $OutFile).Length }
    if ($drive.AvailableFreeSpace -lt $need) { $pr.Close(); Fail ("Not enough free space on drive {0}: about {1:N1} GB are needed." -f $drive.Name, ($dstSize / 1GB)) }

    Write-Host "Step 3 of 5: copying your disc file to the new file (about a minute)..."
    [System.IO.File]::Copy($Original, $OutFile, $true)
    [System.IO.File]::SetAttributes($OutFile, [System.IO.FileAttributes]::Normal)

    Write-Host "Step 4 of 5: writing the two-player changes ($runs places)..."
    $out = [System.IO.File]::Open($OutFile, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    try {
        if ($out.Length -ne $dstSize) { $out.SetLength($dstSize) }
        $buf = New-Object byte[] (1MB)
        for ($i = 0; $i -lt $runs; $i++) {
            $first = [int64]$pr.ReadUInt32()
            $count = [int64]$pr.ReadUInt32()
            $left = $count * $sector
            $out.Position = $first * $sector
            while ($left -gt 0) {
                $want = [int][Math]::Min([int64]$buf.Length, $left)
                $n = $ps.Read($buf, 0, $want)
                if ($n -le 0) { throw "the patch file ends too early" }
                $out.Write($buf, 0, $n)
                $left -= $n
            }
        }
        $out.Flush()
    } finally {
        $out.Close()
        $pr.Close()
    }

    Write-Host "Step 5 of 5: checking the new file (about a minute)..."
    $got = FileSha1 $OutFile
    if ($got -ne $dstSha) {
        Remove-Item -LiteralPath $OutFile -Force
        Fail "The new file came out wrong (check number $got, expected $dstSha). It was deleted. Try again; if it happens again, send this text."
    }
    Write-Host ""
    Write-Host "OK. The two-player test disc is ready:" -ForegroundColor Green
    Write-Host "  $OutFile"
    Write-Host "Its check number (SHA-1) is $got"
    Write-Host "Both players must get exactly this check number."
    Finish 0
} catch {
    Fail ("Unexpected problem: " + $_.Exception.Message)
}
