"""Make the two patch files the test package ships (patches/test-package-v3):
  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v18-own) + the official widescreen group
  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v18) + the same group
The widescreen group is the one lane T took from the emulator's own patch collection (patches/lane-t-kh2test).

  python -I tools/package/make_package_patch.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
NAME = "SLPM-66675_F266B00B.pnach"
old = (ROOT / "patches" / "lane-t-kh2test" / NAME).read_text(encoding="ascii")
tail = old[old.index("[Widescreen 16:9]"):]


def make(src, dst, what):
    lines = [l for l in (ROOT / src).read_text(encoding="ascii").splitlines() if l.startswith("patch=")]
    head = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
            "comment=Two-player project, %s." % what,
            "comment=TEST PACKAGE copy: the two-player patch plus the official widescreen group below.",
            "comment=Every PC in an online game must have this same file (it changes game code)."]
    d = ROOT / dst
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text("\n".join(head + lines) + "\n\n" + tail, encoding="ascii", newline="\n")
    print(dst, len(lines), "lines")


make("patches/merged-v18-own/" + NAME, "patches/test-package-v3/" + NAME,
     "OWN SCREENS build (patches/merged-v18-own, tools/own/make_own.py --base merged-v18 --cannon2view)")
make("patches/merged-v18/" + NAME, "patches/test-package-v3/shared/" + NAME,
     "SHARED SCREEN build = merged build 6 (tools/merge/merge_v6.py)")
