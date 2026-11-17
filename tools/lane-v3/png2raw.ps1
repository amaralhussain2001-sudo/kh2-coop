# Convert a PNG to a simple raw file for the comparison script: 8 bytes header (width, height as 32-bit little
# endian) then width*height*4 bytes BGRA, top row first. Optionally resample to a given size first (high quality).
# Usage: powershell -File tools\lane-v3\png2raw.ps1 -In a.png -Out a.raw [-W 1194 -H 896]
param([string]$In, [string]$Out, [int]$W = 0, [int]$H = 0)
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile($In)
if ($W -le 0) { $W = $src.Width }
if ($H -le 0) { $H = $src.Height }
$bmp = New-Object System.Drawing.Bitmap $W, $H, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $W, $H), (New-Object System.Drawing.Rectangle 0, 0, $src.Width, $src.Height), [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$rect = New-Object System.Drawing.Rectangle 0, 0, $W, $H
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$bytes = New-Object byte[] ($W * $H * 4)
for ($y = 0; $y -lt $H; $y++) {
    [System.Runtime.InteropServices.Marshal]::Copy([IntPtr]($data.Scan0.ToInt64() + $y * $data.Stride), $bytes, $y * $W * 4, $W * 4)
}
$bmp.UnlockBits($data)
$fs = [System.IO.File]::Create($Out)
$fs.Write([BitConverter]::GetBytes([int]$W), 0, 4); $fs.Write([BitConverter]::GetBytes([int]$H), 0, 4)
$fs.Write($bytes, 0, $bytes.Length); $fs.Close()
$bmp.Dispose(); $src.Dispose()
"$Out : ${W}x${H} from $($In | Split-Path -Leaf)"
