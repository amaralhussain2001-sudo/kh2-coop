# Lane V2 acceptance check: does the HUD of one player's view, stretched back to full width, sit at the same
# place and have the same size as the HUD of a one-view picture?
#
#   powershell -File hudmatch.ps1 -Ref <one-view.png> -Two <two-view.png> -Side L|R -Rects "name=x,y,w,h;..." -Out <report.txt> [-Sheet <png>]
#
# -Two is a side-by-side picture (each half = a complete view squeezed to half width). The chosen half is stretched
# to the full width (what the emulator does for that player) and compared with -Ref inside every rectangle
# (rectangle = a HUD part, in pixels of the reference picture). For every rectangle the tool searches the shift
# (dx, dy within +-12 pixels) and the size factors (0.90 .. 1.10 in both directions) that make the two pictures
# agree best. "Same place and size" = the best agreement is at shift 0 and factor 1.00.
# -Two may also be a one-view picture with -Side F (full): it is then compared as it is (control run).
param([string]$Ref, [string]$Two, [string]$Side = "R", [string]$Rects, [string]$Out, [string]$Sheet = "")

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class HudMatch {
    public static float[,] Gray(string path, out int w, out int h) {
        using (Bitmap b0 = new Bitmap(path)) {
            w = b0.Width; h = b0.Height;
            using (Bitmap b = b0.Clone(new Rectangle(0, 0, w, h), PixelFormat.Format24bppRgb)) {
                BitmapData d = b.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                byte[] raw = new byte[d.Stride * h];
                Marshal.Copy(d.Scan0, raw, 0, raw.Length);
                b.UnlockBits(d);
                float[,] g = new float[h, w];
                for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
                    int i = y * d.Stride + x * 3;
                    g[y, x] = 0.114f * raw[i] + 0.587f * raw[i + 1] + 0.299f * raw[i + 2];
                }
                return g;
            }
        }
    }
    // the chosen half stretched to the full width (linear in x)
    public static float[,] Stretch(float[,] g, int w, int h, string side) {
        if (side == "F") return g;
        float[,] o = new float[h, w];
        int half = w / 2, x0 = side == "L" ? 0 : half;
        for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
            float fx = (x + 0.5f) / 2f - 0.5f; if (fx < 0) fx = 0; if (fx > half - 1) fx = half - 1;
            int xi = (int)fx; float t = fx - xi; int xj = Math.Min(xi + 1, half - 1);
            o[y, x] = g[y, x0 + xi] * (1 - t) + g[y, x0 + xj] * t;
        }
        return o;
    }
    static float Sample(float[,] g, int w, int h, float x, float y) {
        if (x < 0) x = 0; if (y < 0) y = 0; if (x > w - 1) x = w - 1; if (y > h - 1) y = h - 1;
        int xi = (int)x, yi = (int)y; int xj = Math.Min(xi + 1, w - 1), yj = Math.Min(yi + 1, h - 1);
        float tx = x - xi, ty = y - yi;
        return (g[yi, xi] * (1 - tx) + g[yi, xj] * tx) * (1 - ty) + (g[yj, xi] * (1 - tx) + g[yj, xj] * tx) * ty;
    }
    // mean absolute difference inside the rectangle for a given shift and size factors (about the rectangle's centre)
    public static double Mad(float[,] a, float[,] b, int w, int h, int rx, int ry, int rw, int rh, float sx, float sy, int dx, int dy) {
        double s = 0; int n = 0; float cx = rx + rw / 2f, cy = ry + rh / 2f;
        for (int y = ry; y < ry + rh; y += 2) for (int x = rx; x < rx + rw; x += 2) {
            float v = Sample(b, w, h, cx + (x - cx) * sx + dx, cy + (y - cy) * sy + dy);
            s += Math.Abs(a[y, x] - v); n++;
        }
        return s / n;
    }
    public static string Search(float[,] a, float[,] b, int w, int h, int rx, int ry, int rw, int rh) {
        double best = 1e9; int bdx = 0, bdy = 0; float bsx = 1, bsy = 1;
        for (int i = -10; i <= 10; i++) {
            float sx = 1f + i * 0.01f;
            for (int dy = -12; dy <= 12; dy++) for (int dx = -12; dx <= 12; dx++) {
                double m = Mad(a, b, w, h, rx, ry, rw, rh, sx, 1f, dx, dy);
                if (m < best - 1e-9 || (Math.Abs(m - best) <= 1e-9 && Math.Abs(dx) + Math.Abs(dy) + Math.Abs(i) < Math.Abs(bdx) + Math.Abs(bdy) + Math.Abs((bsx - 1f) * 100f))) { best = m; bdx = dx; bdy = dy; bsx = sx; }
            }
        }
        for (int i = -10; i <= 10; i++) {
            float sy = 1f + i * 0.01f;
            for (int dy = -3; dy <= 3; dy++) {
                double m = Mad(a, b, w, h, rx, ry, rw, rh, bsx, sy, bdx, bdy + dy);
                if (m < best - 1e-9) { best = m; bsy = sy; bdy = bdy + dy; }
            }
        }
        double ident = Mad(a, b, w, h, rx, ry, rw, rh, 1f, 1f, 0, 0);
        bool ok = Math.Abs(bdx) <= 2 && Math.Abs(bdy) <= 1 && Math.Abs(bsx - 1f) < 0.015f && Math.Abs(bsy - 1f) < 0.015f;
        return String.Format(System.Globalization.CultureInfo.InvariantCulture,
            "best fit: shift x {0,3} y {1,3} px, size factor x {2:0.00} y {3:0.00}, mean difference {4,6:0.00}; as it is (no shift, factor 1): {5,6:0.00}  ->  {6}",
            bdx, bdy, bsx, bsy, best, ident, ok ? "SAME PLACE AND SIZE" : "DIFFERENT");
    }
}
"@

$w = 0; $h = 0; $w2 = 0; $h2 = 0
$a = [HudMatch]::Gray($Ref, [ref]$w, [ref]$h)
$b0 = [HudMatch]::Gray($Two, [ref]$w2, [ref]$h2)
if ($w -ne $w2 -or $h -ne $h2) { throw "pictures differ in size: $w x $h and $w2 x $h2" }
$b = [HudMatch]::Stretch($b0, $w, $h, $Side)
$lines = @("reference (one view): $Ref", "compared: $Two, side $Side (L = left half = player 2, R = right half = player 1, F = whole picture), stretched to full width", "picture size $w x $h")
foreach ($r in $Rects.Split(";")) {
    if (-not $r) { continue }
    $name, $nums = $r.Split("=")
    $n = $nums.Split(",") | ForEach-Object { [int]$_ }
    $res = [HudMatch]::Search($a, $b, $w, $h, $n[0], $n[1], $n[2], $n[3])
    $lines += ("{0,-12} rect {1,4},{2,4} {3,4}x{4,4}: {5}" -f $name, $n[0], $n[1], $n[2], $n[3], $res)
}
$lines | Out-File -Encoding utf8 $Out
$lines | ForEach-Object { Write-Output $_ }

if ($Sheet) {
    Add-Type -AssemblyName System.Drawing
    $bmpRef = New-Object System.Drawing.Bitmap $Ref
    $bmpTwo = New-Object System.Drawing.Bitmap $Two
    $bmpOut = New-Object System.Drawing.Bitmap ($w, ($h * 2))
    $g = [System.Drawing.Graphics]::FromImage($bmpOut)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::Bilinear
    $g.DrawImage($bmpRef, 0, 0, $w, $h)
    if ($Side -eq "F") { $src = New-Object System.Drawing.Rectangle (0, 0, $w, $h) }
    elseif ($Side -eq "L") { $src = New-Object System.Drawing.Rectangle (0, 0, [int]($w / 2), $h) }
    else { $src = New-Object System.Drawing.Rectangle ([int]($w / 2), 0, [int]($w / 2), $h) }
    $dst = New-Object System.Drawing.Rectangle (0, $h, $w, $h)
    $g.DrawImage($bmpTwo, $dst, $src, [System.Drawing.GraphicsUnit]::Pixel)
    $g.Dispose(); $bmpOut.Save($Sheet, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmpOut.Dispose(); $bmpRef.Dispose(); $bmpTwo.Dispose()
    Write-Output "sheet (top: reference, bottom: the view stretched back): $Sheet"
}
