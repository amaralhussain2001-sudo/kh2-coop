param([string]$Src, [string]$Out, [int]$X, [int]$Y, [int]$W, [int]$H, [int]$K = 3)
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($Src)
$bmp = New-Object System.Drawing.Bitmap ($W * $K), ($H * $K)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($im, (New-Object System.Drawing.Rectangle 0, 0, ($W * $K), ($H * $K)), (New-Object System.Drawing.Rectangle $X, $Y, $W, $H), [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $im.Dispose()
Write-Output "saved $Out"
