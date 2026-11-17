# Lane K: for each screenshot print a hash of its LEFT half and of its RIGHT half (the two views of the side-by-side
# demo), ignoring the lowest part and the outer edges where the HUD sits.
# Usage: powershell -File tools\lane-k\halfhash.ps1 -Dir <folder> -Pattern "p1_f0050*.png"
param([string]$Dir, [string]$Pattern = "p1_f*.png")
Add-Type -AssemblyName System.Drawing
$md5 = [System.Security.Cryptography.MD5]::Create()
function HalfHash($bmp, $x0, $x1, $y0, $y1) {
    $ms = New-Object System.IO.MemoryStream
    for ($y = $y0; $y -lt $y1; $y += 4) {
        for ($x = $x0; $x -lt $x1; $x += 4) {
            $c = $bmp.GetPixel($x, $y)
            $ms.WriteByte($c.R); $ms.WriteByte($c.G); $ms.WriteByte($c.B)
        }
    }
    $h = $md5.ComputeHash($ms.ToArray())
    return ([System.BitConverter]::ToString($h)).Replace("-", "").Substring(0, 8)
}
$files = Get-ChildItem -Path $Dir -Filter $Pattern | Sort-Object Name
foreach ($f in $files) {
    $bmp = New-Object System.Drawing.Bitmap $f.FullName
    $w = $bmp.Width; $h = $bmp.Height
    # middle band of each half: away from the HUD corners
    $l = HalfHash $bmp ([int]($w * 0.30)) ([int]($w * 0.49)) ([int]($h * 0.10)) ([int]($h * 0.55))
    $r = HalfHash $bmp ([int]($w * 0.51)) ([int]($w * 0.80)) ([int]($h * 0.10)) ([int]($h * 0.55))
    "{0} left {1} right {2}" -f $f.BaseName, $l, $r
    $bmp.Dispose()
}
