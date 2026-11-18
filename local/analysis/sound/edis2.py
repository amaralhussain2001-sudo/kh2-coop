"""Read-only: disassemble the game ELF (SLPM_666.75) with COP1 (float) and COP2 (VU0 macro) decoded.
  python -I edis2.py <startHex> <endHex>
Also importable: dis2(word, pc)."""
import pathlib, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips

F1S = {0: "add.s", 1: "sub.s", 2: "mul.s", 3: "div.s", 4: "sqrt.s", 5: "abs.s", 6: "mov.s", 7: "neg.s", 0x16: "rsqrt.s",
       0x18: "adda.s", 0x19: "suba.s", 0x1A: "mula.s", 0x1C: "madd.s", 0x1D: "msub.s", 0x1E: "madda.s", 0x1F: "msuba.s",
       0x24: "cvt.w.s", 0x28: "max.s", 0x29: "min.s", 0x30: "c.f.s", 0x32: "c.eq.s", 0x34: "c.lt.s", 0x36: "c.le.s"}
BC = "xyzw"
SP1 = {}
for k, n in ((0x00, "vadd"), (0x04, "vsub"), (0x08, "vmadd"), (0x0C, "vmsub"), (0x10, "vmax"), (0x14, "vmini"), (0x18, "vmul")):
    for b in range(4):
        SP1[k + b] = n + BC[b]
SP1.update({0x1C: "vmulq", 0x1D: "vmaxi", 0x1E: "vmuli", 0x1F: "vminii", 0x20: "vaddq", 0x21: "vmaddq", 0x22: "vaddi",
            0x23: "vmaddi", 0x24: "vsubq", 0x25: "vmsubq", 0x26: "vsubi", 0x27: "vmsubi", 0x28: "vadd", 0x29: "vmadd",
            0x2A: "vmul", 0x2B: "vmax", 0x2C: "vsub", 0x2D: "vmsub", 0x2E: "vopmsub", 0x2F: "vmini", 0x30: "viadd",
            0x31: "visub", 0x32: "viaddi", 0x34: "viand", 0x35: "vior", 0x38: "vcallms", 0x39: "vcallmsr"})
SP2 = {}
for k, n in ((0x00, "vadda"), (0x04, "vsuba"), (0x08, "vmadda"), (0x0C, "vmsuba"), (0x18, "vmula")):
    for b in range(4):
        SP2[k + b] = n + BC[b]
SP2.update({0x10: "vitof0", 0x11: "vitof4", 0x12: "vitof12", 0x13: "vitof15", 0x14: "vftoi0", 0x15: "vftoi4",
            0x16: "vftoi12", 0x17: "vftoi15", 0x1C: "vmulaq", 0x1D: "vabs", 0x1E: "vmulai", 0x1F: "vclipw",
            0x20: "vaddaq", 0x21: "vmaddaq", 0x22: "vaddai", 0x23: "vmaddai", 0x24: "vsubaq", 0x25: "vmsubaq",
            0x26: "vsubai", 0x27: "vmsubai", 0x28: "vadda", 0x29: "vmadda", 0x2A: "vmula", 0x2C: "vsuba",
            0x2D: "vmsuba", 0x2E: "vopmula", 0x2F: "vnop", 0x30: "vmove", 0x31: "vmr32", 0x34: "vlqi", 0x35: "vsqi",
            0x36: "vlqd", 0x37: "vsqd", 0x38: "vdiv", 0x39: "vsqrt", 0x3A: "vrsqrt", 0x3B: "vwaitq", 0x3C: "vmtir",
            0x3D: "vmfir", 0x3E: "vilwr", 0x3F: "viswr", 0x40: "vrnext", 0x41: "vrget", 0x42: "vrinit", 0x43: "vrxor"})


def dis2(w, pc):
    op, rs = w >> 26, (w >> 21) & 31
    ft, fs, fd, fn = (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
    if op == 0x11 and rs == 0x10 and fn in F1S:
        n = F1S[fn]
        if fn in (4, 5, 6, 7, 0x24):
            return f"{n} f{fd},f{fs}"
        if fn >= 0x30 or fn in (0x18, 0x19, 0x1A, 0x1E, 0x1F):
            return f"{n} f{fs},f{ft}"
        if fn == 0x16:
            return f"{n} f{fd},f{fs},f{ft}"
        return f"{n} f{fd},f{fs},f{ft}"
    if op == 0x11 and rs == 0x14 and fn == 0x20:
        return f"cvt.s.w f{fd},f{fs}"
    if op == 0x11 and rs in (2, 6):
        return f"{'cfc1' if rs == 2 else 'ctc1'} {mips.R[ft]},${fs}"
    if op == 0x12:
        dest = "".join(c for i, c in enumerate("xyzw") if w & (1 << (24 - i)))
        if rs >= 0x10:
            if fn < 0x3C:
                n = SP1.get(fn, "vu?%02X" % fn)
                if n.startswith("vi"):
                    return f"{n} vi{fd},vi{fs},vi{ft}"
                return f"{n}.{dest} vf{fd},vf{fs},vf{ft}"
            x = (((w >> 6) & 0x1F) << 2) | (w & 3)
            n = SP2.get(x, "vu2?%02X" % x)
            if n in ("vdiv", "vsqrt", "vrsqrt"):
                fsf, ftf = "xyzw"[(w >> 21) & 3], "xyzw"[(w >> 23) & 3]
                return f"{n} Q,vf{fs}{fsf},vf{ft}{ftf}"
            return f"{n}.{dest} vf{ft},vf{fs}"
        names = {1: "qmfc2", 2: "cfc2", 5: "qmtc2", 6: "ctc2"}
        if rs in names:
            return f"{names[rs]} {mips.R[ft]},vf{fs}" if rs in (1, 5) else f"{names[rs]} {mips.R[ft]},vi{fs}"
    if op == 0x36:
        return f"lqc2 vf{ft},{mips.s16(w & 0xFFFF)}({mips.R[rs]})"
    if op == 0x3E:
        return f"sqc2 vf{ft},{mips.s16(w & 0xFFFF)}({mips.R[rs]})"
    if op == 0x1E:
        return f"lq {mips.R[ft]},{mips.s16(w & 0xFFFF)}({mips.R[rs]})"
    if op == 0x1F:
        return f"sq {mips.R[ft]},{mips.s16(w & 0xFFFF)}({mips.R[rs]})"
    return mips.dis(w, pc)


ELF = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))

if __name__ == "__main__":
    a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
    for pc in range(a, b, 4):
        w = ELF.word(pc)
        print("%08X  %08X  %s" % (pc, w, dis2(w, pc)))
