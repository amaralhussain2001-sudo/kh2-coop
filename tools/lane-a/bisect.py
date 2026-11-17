"""Lane A: make experiment patch files that switch chosen calls of the controller getter (0x00167F18) from
controller index 0 to index 1 by replacing 'a0 = 0' (daddu a0,zero,zero) with 'a0 = 1' (addiu a0,zero,1).

  python -I tools/lane-a/bisect.py list <elf>
  python -I tools/lane-a/bisect.py bits <elf> <outRoot>            -> <outRoot>/bit0..bit5/SLPM-66675_F266B00B.pnach
  python -I tools/lane-a/bisect.py sites <elf> <outDir> <idx,idx,...>   -> one patch file with exactly these sites
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

GETTER = 0x00167F18
A0_ZERO = 0x0000202D   # daddu a0,zero,zero
A0_ONE = 0x24040001    # addiu a0,zero,1


def sites(elf_path):
    e = mips.Elf(elf_path)
    va, off, fs = e.segs[0]
    words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
    jal = mips.jal(GETTER)
    out = []
    for i, w in enumerate(words):
        if w != jal:
            continue
        where = None
        for k in [i + 1] + list(range(i - 1, i - 8, -1)):
            if words[k] == A0_ZERO:
                where = va + 4 * k
                break
        out.append((va + 4 * i, where))
    return out


def write_pnach(outdir, chosen, note):
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B) - lane A experiment",
             "comment=EXPERIMENT ONLY: " + note]
    for call, where in chosen:
        lines.append(f"patch=1,EE,{where:08X},word,{A0_ONE:08X}")
    (outdir / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")


def main():
    cmd, elf = sys.argv[1], sys.argv[2]
    s = sites(elf)
    usable = [(i, c, w) for i, (c, w) in enumerate(s) if w is not None]
    if cmd == "list":
        for i, (c, w) in enumerate(s):
            print(i, f"call 0x{c:08X}", f"a0=0 at 0x{w:08X}" if w else "no simple a0=0")
    elif cmd == "bits":
        root = pathlib.Path(sys.argv[3])
        for b in range(6):
            chosen = [(c, w) for i, c, w in usable if (i >> b) & 1]
            write_pnach(root / f"bit{b}", chosen, f"getter calls whose index has bit {b} set use controller 2 ({len(chosen)} sites)")
            print(f"bit{b}: {len(chosen)} sites")
    elif cmd == "sites":
        idx = {int(x) for x in sys.argv[4].split(",")}
        chosen = [(c, w) for i, c, w in usable if i in idx]
        write_pnach(sys.argv[3], chosen, "getter calls " + ",".join(f"0x{c:08X}" for c, w in chosen) + " use controller 2")
        print("sites:", [f"{i}:0x{c:08X}" for i, c, w in usable if i in idx])


if __name__ == "__main__":
    main()
