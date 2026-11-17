# Build emulator/pcsx2 (PCSX2 v2.9.115 + our changes) with MSVC from Visual Studio Build Tools.
# Usage: powershell -File emulator\build.ps1 [-Config Release] [-Log <file>]
param([string]$Config = "Release", [string]$Log = "")
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "pcsx2"
$vsInstaller = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer"
$env:PATH = "$vsInstaller;$env:PATH"
$vsPath = & "$vsInstaller\vswhere.exe" -latest -products * -property installationPath
if (-not $vsPath) { throw "Visual Studio Build Tools not found" }
$vcvars = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
$msbuild = Join-Path $vsPath "MSBuild\Current\Bin\MSBuild.exe"
if ($Log -eq "") {
    $logDir = Join-Path $PSScriptRoot "..\local\logs"
    New-Item -ItemType Directory -Force $logDir | Out-Null
    $Log = Join-Path $logDir "build_$Config.log"
}
$started = Get-Date
cmd /c "call `"$vcvars`" >nul && `"$msbuild`" `"$src\PCSX2_qt.slnx`" /m /nologo /v:minimal /p:Configuration=$Config /p:Platform=x64 /t:pcsx2-qt" *> $Log
$code = $LASTEXITCODE
$mins = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
"exit=$code minutes=$mins log=$Log"
exit $code
