# Put many screenshots into one labelled image, to look at a test quickly.
# Usage: powershell -File tools\contact_sheet.ps1 -Dir <folder> -Pattern "p1_f*.png" -Out sheet.png [-Cols 6] [-Width 320]
param([string]$Dir, [string]$Pattern = "*.png", [string]$Out, [int]$Cols = 6, [int]$Width = 320)
Add-Type -AssemblyName System.Drawing
$files = Get-ChildItem -Path $Dir -Filter $Pattern | Where-Object { $_.Name -notlike "sheet*" } | Sort-Object Name
if ($files.Count -eq 0) { "no files"; exit 1 }
$first = [System.Drawing.Image]::FromFile($files[0].FullName)
$h = [int]($first.Height * $Width / $first.Width)
$first.Dispose()
$rows = [math]::Ceiling($files.Count / $Cols)
$sheet = New-Object System.Drawing.Bitmap ($Cols * $Width), ($rows * ($h + 18))
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.Clear([System.Drawing.Color]::FromArgb(40, 40, 40))
$font = New-Object System.Drawing.Font "Arial", 9
$i = 0
foreach ($f in $files) {
    $img = [System.Drawing.Image]::FromFile($f.FullName)
    $x = ($i % $Cols) * $Width
    $y = [math]::Floor($i / $Cols) * ($h + 18)
    $g.DrawImage($img, $x, $y + 18, $Width, $h)
    $g.DrawString($f.BaseName, $font, [System.Drawing.Brushes]::White, $x + 2, $y + 2)
    $img.Dispose()
    $i++
}
$sheet.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $sheet.Dispose()
"sheet: $Out ($($files.Count) images)"
