"""One-off: tools/own/holdsum.py and holdline.py also read the timelines of cap_log_probe.py / cap_log_probe2.py
(lines that start with "act " and may carry "held N hook N" in front of the place). Run once."""
import pathlib

here = pathlib.Path(__file__).resolve().parent
old = 'LINE = re.compile(r"^f(\d+) P1 a([0-9A-F]+) (\([^)]*\)).*?\| P2 a([0-9A-F]+) (\([^)]*\))")'
new = 'LINE = re.compile(r"^(?:act )?f(\d+) P1 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\)).*?\| P2 a([0-9A-F]+) (?:held \d hook \d )?(\([^)]*\))")'
for name in ("holdsum.py", "holdline.py"):
    p = here / name
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (name, s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline=chr(10))
print("ok")
