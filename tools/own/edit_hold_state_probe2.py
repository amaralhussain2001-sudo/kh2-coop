"""One-off: tools/own/hold_state_probe.py also prints, for each hero: the parent he is attached to (object + 0x570),
the script flag words (object + 0x108, + 0x10C), the state object's first words (object + 0x0C), the motion part's
words (object + 0x140 .. + 0x15F and + 0x1D0 .. + 0x1DF = part + 0x90). Run once."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "hold_state_probe.py"
s = p.read_text(encoding="utf-8")
assert "attached to" not in s
a = '''    return "%08X a%02X held %d captor word %08X hook %08X flags160 %08X HP %s at (%s)" % (
        o, p.r32(o + 0x154) & 0xFFFF, (p.r32(o + 0x160) >> 14) & 1, p.r32(o + 0x240), p.r32(o + 0xAEC), p.r32(o + 0x160), hp,
        ", ".join("%.0f" % v for v in struct.unpack("<3f", p.read(o + 0x70, 12))))
'''
assert s.count(a) == 1
b = '''    st = p.r32(o + 0x0C)
    more = " | attached to %08X script flags %08X %08X state object %08X: %s | motion part: %s | part+0x90: %s" % (
        p.r32(o + 0x570), p.r32(o + 0x108), p.r32(o + 0x10C), st,
        " ".join("%08X" % w for w in struct.unpack("<6I", p.read(st, 24))) if ok(st) else "-",
        " ".join("%08X" % w for w in struct.unpack("<8I", p.read(o + 0x140, 32))),
        " ".join("%08X" % w for w in struct.unpack("<4I", p.read(o + 0x1D0, 16))))
    return "%08X a%02X held %d captor word %08X hook %08X flags160 %08X HP %s at (%s)" % (
        o, p.r32(o + 0x154) & 0xFFFF, (p.r32(o + 0x160) >> 14) & 1, p.r32(o + 0x240), p.r32(o + 0xAEC), p.r32(o + 0x160), hp,
        ", ".join("%.0f" % v for v in struct.unpack("<3f", p.read(o + 0x70, 12)))) + more
'''
s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
