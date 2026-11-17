# Put pictures next to each other with a caption under each, for comparing by eye.
# Usage: powershell -File tools\lane-v3\sheet.ps1 -Out sheet.png -Items "caption one|a.png","caption two|b.png" [-CellWidth 560]
param([string]$Out, [string[]]$Items, [int]$CellWidth = 560)
Add-Type -AssemblyName System.Drawing
$pics = @()
foreach ($it in $Items) {
    $cut = $it.IndexOf('|')
    $pics += [pscustomobject]@{ Text = $it.Substring(0, $cut); Img = [System.Drawing.Image]::FromFile($it.Substring($cut + 1)) }
}
$pad = 8; $cap = 26
$cellH = 0
foreach ($p in $pics) { $h = [int]($p.Img.Height * $CellWidth / $p.Img.Width); if ($h -gt $cellH) { $cellH = $h } }
$w = $pad + $pics.Count * ($CellWidth + $pad)
$h = $pad + $cellH + $cap + $pad
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::FromArgb(32, 32, 32))
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font = New-Object System.Drawing.Font "Segoe UI", 11
$x = $pad
foreach ($p in $pics) {
    $ph = [int]($p.Img.Height * $CellWidth / $p.Img.Width)
    $g.DrawImage($p.Img, $x, $pad, $CellWidth, $ph)
    $g.DrawString($p.Text, $font, [System.Drawing.Brushes]::White, $x, $pad + $cellH + 3)
    $x += $CellWidth + $pad
    $p.Img.Dispose()
}
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"$Out : ${w}x${h}"
