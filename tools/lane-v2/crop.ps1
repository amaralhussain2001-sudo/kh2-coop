# Lane V2: cut a rectangle out of screenshots and put the pieces side by side (to look at a HUD corner closely).
# usage: powershell -File crop.ps1 -Dir <folder> -Pattern "p1_f*.png" -X 880 -Y 480 -W 360 -H 450 -Out crop.png [-Zoom 2]
param([string]$Dir, [string]$Pattern = "p1_f*.png", [int]$X, [int]$Y, [int]$W, [int]$H, [string]$Out, [int]$Zoom = 1)
Add-Type -AssemblyName System.Drawing
$files = Get-ChildItem -Path $Dir -Filter $Pattern | Where-Object { $_.Name -notlike "sheet*" -and $_.Name -notlike "crop*" } | Sort-Object Name
if ($files.Count -eq 0) { "no files"; exit 1 }
$sheet = New-Object System.Drawing.Bitmap ($files.Count * $W * $Zoom), ($H * $Zoom + 18)
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.Clear([System.Drawing.Color]::FromArgb(40, 40, 40))
$font = New-Object System.Drawing.Font "Arial", 9
$i = 0
foreach ($f in $files) {
    $img = [System.Drawing.Image]::FromFile($f.FullName)
    $src = New-Object System.Drawing.Rectangle $X, $Y, $W, $H
    $dst = New-Object System.Drawing.Rectangle ($i * $W * $Zoom), 18, ($W * $Zoom), ($H * $Zoom)
    $g.DrawImage($img, $dst, $src, [System.Drawing.GraphicsUnit]::Pixel)
    $g.DrawString($f.BaseName, $font, [System.Drawing.Brushes]::White, ($i * $W * $Zoom + 2), 2)
    $img.Dispose()
    $i++
}
$sheet.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $sheet.Dispose()
"crop sheet: $Out ($($files.Count) images)"
