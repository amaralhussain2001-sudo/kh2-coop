"""Read-only: disassemble the game ELF (SLPM_666.75) range, with patched words from a listing marked.
  python -I edis.py <startHex> <endHex> [listing]"""
import pathlib, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips
elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
pat = {}
lst = ROOT / "patches" / "merged-v20-own" / "listing.txt"
for line in open(lst, encoding="utf-8", errors="replace"):
    p = line.split(None, 2)
    if len(p) >= 2 and len(p[0]) == 8:
        try:
            pat[int(p[0], 16)] = (int(p[1], 16), p[2].strip() if len(p) > 2 else "")
        except ValueError:
            pass
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
for pc in range(a, b, 4):
    w = elf.word(pc)
    tag = ""
    if pc in pat:
        pw, why = pat[pc]
        tag = "   <<PATCHED %08X %s | %s" % (pw, mips.dis(pw, pc), why[:70])
    print("%08X  %08X  %-40s%s" % (pc, w if w is not None else 0, mips.dis(w, pc) if w is not None else "?", tag))
