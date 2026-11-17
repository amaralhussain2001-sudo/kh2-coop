"""The controller fix of the test package (2026-11-16, STATE part 127): the user's pad, a GameSir in Xbox mode (Windows: "Xbox Gaming
Device"), was not seen by the emulator, whose only controller route was SDL ([InputSources] XInput = false; its log opened no gamepad).
This turns the XInput route on and gives controller port 1 the first XInput pad as well (XInput-0), beside its keyboard and SDL-0
bindings: Triangle = Y, Circle = B, Cross = A, Square = X, the sticks, shoulders, triggers, Start / Select. The join check of the
two-player emulator (PS2Net.cpp SettingsFingerprint) does not compare [InputSources] nor the bindings, so PCs with and without it
still join each other. Used by make_test_package.py after it copies PCSX2.ini; can be run on a finished package:
  python -I tools/package/xinput_fix.py <path to emulator\\inis\\PCSX2.ini>
"""
import re
import sys

XMAP = {"DPadUp": "DPadUp", "DPadRight": "DPadRight", "DPadDown": "DPadDown", "DPadLeft": "DPadLeft", "FaceNorth": "Y",
        "FaceEast": "B", "FaceSouth": "A", "FaceWest": "X", "Back": "Back", "Start": "Start", "LeftShoulder": "LeftShoulder",
        "RightShoulder": "RightShoulder", "+LeftTrigger": "+LeftTrigger", "+RightTrigger": "+RightTrigger",
        "LeftStick": "LeftStick", "RightStick": "RightStick", "-LeftY": "-LeftY", "+LeftY": "+LeftY", "-LeftX": "-LeftX",
        "+LeftX": "+LeftX", "-RightY": "-RightY", "+RightY": "+RightY", "-RightX": "-RightX", "+RightX": "+RightX",
        "Guide": "Guide", "LargeMotor": "LargeMotor", "SmallMotor": "SmallMotor"}


def add_xinput(path):
    """Returns the number of XInput-0 bindings added (0 if the file had them already)."""
    raw = open(path, "rb").read()
    bom, crlf = raw.startswith(b"\xef\xbb\xbf"), b"\r\n" in raw
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    if "XInput-0/" in text:
        return 0
    out, sec, added = [], "", 0
    for line in text.split("\n"):
        m = re.match(r"^\[(.+)\]$", line.strip())
        if m:
            sec = m.group(1)
        if sec == "InputSources" and line.startswith("XInput ="):
            line = "XInput = true"
        out.append(line)
        m = re.match(r"^(\w+) = SDL-0/(\S+)$", line)
        if sec == "Pad1" and m and m.group(2) in XMAP:
            out.append("%s = XInput-0/%s" % (m.group(1), XMAP[m.group(2)]))
            added += 1
    text = "\n".join(out)
    if crlf:
        text = text.replace("\n", "\r\n")
    open(path, "wb").write((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    return added


if __name__ == "__main__":
    print("XInput-0 bindings added:", add_xinput(sys.argv[1]))
