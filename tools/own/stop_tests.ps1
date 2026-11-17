# Stops every running test of this project: the suite / batch shell scripts, the session scripts and the test
# emulators of the sandboxes local\run-m, local\run-v3, local\run-v3b. Nothing else is touched.
# usage: powershell -File tools\own\stop_tests.ps1
$names = 'suite_v6\.sh|suite_v5_short\.sh|suite_v5\.sh|batch_v6\.sh|batch_v7\.sh|mrun\.sh|mrecrun\.sh|run_own\.sh|run_own2\.sh|dusk_one\.sh|two_tests\.sh|rules_bits\.sh|near_batch\.sh|final_b8\.sh|final_b9\.sh|final_b10\.sh|final_b11\.sh|final_b12\.sh|sweep\.sh|kh2_session\.py|v3_session\.py|mrec\.py|_probe\.py|drv_probe2\.py'
$all = Get-CimInstance Win32_Process
foreach ($p in $all) {
    if (-not $p.CommandLine) { continue }
    $hit = $false
    if ($p.CommandLine -match $names) { $hit = $true }
    if ($p.Name -match 'pcsx2' -and $p.CommandLine -match 'run-m|run-v3') { $hit = $true }
    if ($hit) {
        try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop } catch {}
    }
}
Start-Sleep -Seconds 2
$left = @(Get-Process | Where-Object { $_.Name -match 'pcsx2' }).Count
Write-Output "test emulators still running: $left"
