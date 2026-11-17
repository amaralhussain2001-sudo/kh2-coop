# Cut a part out of a picture (given as fractions of its size) and save it, optionally enlarged without smoothing,
# so pictures taken at different internal resolutions can be compared by eye.
# Usage: powershell -File tools\lane-v3\crop.ps1 -In a.png -Out b.png -X 0.3 -Y 0.4 -W 0.25 -H 0.25 [-OutWidth 800]
param([string]$In, [string]$Out, [double]$X = 0, [double]$Y = 0, [double]$W = 1, [double]$H = 1, [int]$OutWidth = 0)
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile($In)
$rx = [int]($src.Width * $X); $ry = [int]($src.Height * $Y)
$rw = [int]($src.Width * $W); $rh = [int]($src.Height * $H)
if ($OutWidth -le 0) { $OutWidth = $rw }
$oh = [int]($rh * $OutWidth / $rw)
$bmp = New-Object System.Drawing.Bitmap $OutWidth, $oh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $OutWidth, $oh), (New-Object System.Drawing.Rectangle $rx, $ry, $rw, $rh), [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $src.Dispose()
"$Out : source ${rw}x${rh} px of $($In | Split-Path -Leaf) shown at ${OutWidth}x${oh}"
