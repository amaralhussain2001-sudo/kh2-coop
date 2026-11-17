# Build emulator-src\pcsx2 (private working copy of the PS2 Online emulator source) with MSVC Build Tools.
# Same command as the original project's emulator\build.ps1, but at BELOW-NORMAL priority (the PC is shared
# with test lanes) and with the log under emulator-src\logs.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File emulator-src\build.ps1 [-Config Release] [-Log <file>]
param([string]$Config = "Release", [string]$Log = "")
$ErrorActionPreference = "Stop"
(Get-Process -Id $PID).PriorityClass = 'BelowNormal'   # child processes inherit this class
$src = Join-Path $PSScriptRoot "pcsx2"
$vsInstaller = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer"
$env:PATH = "$vsInstaller;$env:PATH"
$vsPath = & "$vsInstaller\vswhere.exe" -latest -products * -property installationPath
if (-not $vsPath) { throw "Visual Studio Build Tools not found" }
$vcvars = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
$msbuild = Join-Path $vsPath "MSBuild\Current\Bin\MSBuild.exe"
if ($Log -eq "") {
    $logDir = Join-Path $PSScriptRoot "logs"
    New-Item -ItemType Directory -Force $logDir | Out-Null
    $Log = Join-Path $logDir "build_$Config.log"
}
New-Item -ItemType Directory -Force (Split-Path -Parent $Log) | Out-Null
$started = Get-Date
cmd /c "call `"$vcvars`" >nul && `"$msbuild`" `"$src\PCSX2_qt.slnx`" /m /nologo /v:minimal /p:Configuration=$Config /p:Platform=x64 /t:pcsx2-qt" *> $Log
$code = $LASTEXITCODE
$mins = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
"exit=$code minutes=$mins log=$Log"
exit $code
