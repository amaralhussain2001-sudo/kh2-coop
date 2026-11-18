import sys, pathlib
ROOT = pathlib.Path(r"C:\Users\PC FORCE\Desktop\New folder (3)")
sys.path.insert(0, str(ROOT / "tools" / "lane-a"))
import mips
elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
for arg in sys.argv[1:]:
    s, e = arg.split("-")
    s, e = int(s, 16), int(e, 16)
    for a in range(s, e, 4):
        w = elf.word(a)
        if w is None:
            print("%08X ????????" % a); continue
        print("%08X %08X  %s" % (a, w, mips.dis(w, a)))
    print()
