"""One-off: tools/own/gscore_probe.py also prints the places (picture + 356 / + 360) of row 2's first and last digit
pictures and of the gauge's digit, and the gauge's first picture's place as the glue noted it (0x000E7F30 / 34)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "gscore_probe.py"
s = p.read_text(encoding="utf-8")
assert "places:" not in s
a = "        lines.append(row)\n"
assert s.count(a) == 1
b = '''        if p.r16(0x01F18014) == 0x636A:
            def place(pic):
                return "(%d, %d)" % struct.unpack("<2i", p.read(pic + 356, 8)) if ok(pic) else "-"
            row += " | places: row 2 digits %s .. %s, mark %s, gauge noted (%d, %d)" % (
                place(p.r32(0x000E7F48)), place(p.r32(0x000E7F60)), place(p.r32(0x000E7F78)),
                struct.unpack("<i", p.read(0x000E7F30, 4))[0], struct.unpack("<i", p.read(0x000E7F34, 4))[0])
'''
s = s.replace(a, b + a)
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
