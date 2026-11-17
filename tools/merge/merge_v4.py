"""Merged build 4 = merged-v3 - the "1P / 2P" markers + lane B75's HP gauge lines.

User decisions 2026-11-10:
  * boss HP limit = A (gauge patch, every boss gets the full +75 %). The boss HP itself is DATA on the disc
    (tools/lane-b75/scale_boss_hp.py --gauge-patch); this patch only makes the enemy HP gauge safe for it.
    A disc with uncapped boss HP must never be played with a patch that lacks these lines.
  * no "1P / 2P" signs over the heroes' heads ("I can see which one is 1P and 2P without the icon"). Lane V2
    delivered both forms: patches/lane-v2-hud1 (gauge + markers, the one inside merged-v3) and
    patches/lane-v2-p2gauge (the gauge alone). The tool swaps the first for the second, word by word.

  python -I tools/merge/merge_v4.py [outDir] [--markers]        (--markers keeps the signs: test builds only)

Checks before writing:
  0. every word that differs between the two lane V2 forms holds lane V2's value in merged-v3 (nobody else
     touched it), so taking the markers out cannot disturb another lane;
  1. no address of the gauge lines is written by merged-v3;
  2. the gauge lines stay inside their own area (cave 0x000F3800-0x000F38AF, three hook pairs);
  3. the three hook pairs replace exactly the instructions that the cave runs again (read from the game program).
Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v4.
"""
import hashlib
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
NAME = "SLPM-66675_F266B00B.pnach"
BASE = ROOT / "patches" / "merged-v3" / NAME
BASE_LISTING = ROOT / "patches" / "merged-v3" / "listing.txt"
V2_MARKERS = ROOT / "patches" / "lane-v2-hud1" / NAME        # merged-v2 + player 2's gauge + markers
V2_PLAIN = ROOT / "patches" / "lane-v2-p2gauge" / NAME       # merged-v2 + player 2's gauge
GAUGE = ROOT / "tools" / "lane-b75" / "data" / "gauge_patch_lines.txt"
GAUGE_SHA1 = "4282e01ab916fdd3e74c852fbfd2f74cb5c5f8a9"      # from docs/lanes/B75-boss-hp.md, section 7
ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})\s*(?://.*)?$")
CAVE = (0x000F3800, 0x000F38AF)
DATA_WORD = 0x000F3FF0
# hook address -> (cave entry, address the cave returns to, instruction the cave runs again in its last delay slot)
HOOKS = {0x00154450: 0x000F3800, 0x00154B98: 0x000F3820, 0x00154C10: 0x000F3868}


def words_of(path):
    order, words = [], {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        if m.group(1) != "1" or m.group(3).lower() != "word":
            raise SystemExit(f"{path.name}: unexpected line kind: {raw}")
        a = int(m.group(2), 16)
        if a in words:
            raise SystemExit(f"{path.name}: address written twice: {a:08X}")
        order.append(a)
        words[a] = int(m.group(4), 16)
    return order, words


def elf_word(data, addr):
    """Read one word of the game program by its memory address (program headers of the ELF)."""
    phoff, = struct.unpack_from("<I", data, 0x1C)
    phentsize, phnum = struct.unpack_from("<HH", data, 0x2A)
    for i in range(phnum):
        p_type, p_offset, p_vaddr, _pa, p_filesz = struct.unpack_from("<IIIII", data, phoff + i * phentsize)
        if p_type == 1 and p_vaddr <= addr < p_vaddr + p_filesz:
            return struct.unpack_from("<I", data, p_offset + addr - p_vaddr)[0]
    raise SystemExit(f"address {addr:08X} is not in the game program file")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = ROOT / (args[0] if args else "patches/merged-v4")
    sha = hashlib.sha1(GAUGE.read_bytes()).hexdigest()
    if sha != GAUGE_SHA1:
        raise SystemExit(f"gauge lines file changed: sha1 {sha}, expected {GAUGE_SHA1}")
    base_o, base = words_of(BASE)
    g_o, g = words_of(GAUGE)

    # 0. take the markers out: lane V2's "gauge + markers" words become its "gauge alone" words
    removed, retargeted = [], []
    if "--markers" not in sys.argv:
        _, with_m = words_of(V2_MARKERS)
        _, plain = words_of(V2_PLAIN)
        if [a for a in plain if a not in with_m]:
            raise SystemExit("lane V2: the gauge-alone form has words the marker form lacks; check by hand")
        for a in sorted(with_m):
            if a in plain and plain[a] == with_m[a]:
                continue
            if base.get(a) != with_m[a]:
                raise SystemExit("marker word %08X: merged-v3 does not hold lane V2's value" % a)
            if a in plain:
                base[a] = plain[a]
                retargeted.append(a)
            else:
                del base[a]
                base_o.remove(a)
                removed.append(a)
        if not (0x000F7240 <= min(removed) and max(removed) <= 0x000F74FF):
            raise SystemExit("marker words outside lane V2's marker area")

    # 1. no address in common
    both = sorted(set(base) & set(g))
    if both:
        raise SystemExit("CLASH: merged-v3 already writes " + ", ".join("%08X" % a for a in both))
    # 2. the gauge lines stay inside their own area
    for a in g_o:
        in_cave = CAVE[0] <= a <= CAVE[1]
        in_hook = any(h <= a < h + 8 for h in HOOKS)
        if not (in_cave or in_hook):
            raise SystemExit("gauge line outside its area: %08X" % a)
    if any(CAVE[0] <= a <= CAVE[1] + 0x50 or a == DATA_WORD for a in base):
        raise SystemExit("merged-v3 writes into the gauge cave or its data word")
    # no merged-v3 word may be a jump or call into the three gauge routines' first two instructions
    for h in HOOKS:
        for target in (h, h + 4):
            for op in (2, 3):
                w = (op << 26) | (target >> 2)
                hit = [a for a in base if base[a] == w]
                if hit:
                    print("NOTE: merged-v3 word at %08X jumps to %08X" % (hit[0], target))
    # 3. the hooks replace what the cave runs again
    elf = ELF.read_bytes()
    checked = []
    for h, entry in HOOKS.items():
        if g[h] != ((2 << 26) | (entry >> 2)):
            raise SystemExit("hook %08X is not 'j %08X'" % (h, entry))
        first, second = elf_word(elf, h), elf_word(elf, h + 4)
        if g[h + 4] != first:
            raise SystemExit("hook %08X: delay slot %08X is not the routine's first instruction %08X" % (h, g[h + 4], first))
        # the cave piece for this hook ends with "j h+8" followed by the routine's second instruction
        back = (2 << 26) | ((h + 8) >> 2)
        ends = [a for a in g_o if CAVE[0] <= a <= CAVE[1] and g[a] == back]
        if len(ends) != 1 or g.get(ends[0] + 4) != second:
            raise SystemExit("hook %08X: the cave does not run the replaced instruction %08X before going back" % (h, second))
        checked.append("%08X: j %08X / %08X ; cave returns to %08X after %08X" % (h, entry, first, h + 8, second))

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, MERGED BUILD 4: merged build 3 (twin on pad 2, own HP, commands, exits,",
        "comment=enemy targeting, down and rescue, gauge for player 2%s) + enemy HP gauge above 3400 HP"
        % (" and 1P/2P markers" if "--markers" in sys.argv else ""),
        "comment=(needed by the disc with bosses +75 % HP). Every PC in an online game must have this same file.",
    ]
    body = ["patch=1,EE,%08X,word,%08X" % (a, base[a]) for a in base_o]
    body += ["patch=1,EE,%08X,word,%08X" % (a, g[a]) for a in g_o]
    (out / NAME).write_text("\n".join(head + body) + "\n", encoding="utf-8")

    origin = {}
    for raw in BASE_LISTING.read_text(encoding="utf-8").splitlines():
        parts = raw.split(None, 2)
        if len(parts) == 3:
            origin[int(parts[0], 16)] = parts[2]
    merged = dict(base)
    merged.update(g)
    for a in g_o:
        origin[a] = "lane B75 (enemy HP gauge above 3400 HP)"
    for a in retargeted:
        origin[a] = "lane V2 (gauge alone: the marker step is taken out)"
    listing = ["%08X %08X  %s" % (a, merged[a], origin.get(a, "merged-v3")) for a in sorted(merged)]
    (out / "listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")

    print("markers: %s" % ("KEPT (--markers)" if "--markers" in sys.argv else
                           "taken out: %d words removed (%08X-%08X), %d hook words back to the gauge-alone routines (%s)"
                           % (len(removed), min(removed), max(removed), len(retargeted),
                              ", ".join("%08X" % a for a in retargeted))))
    print("base words:", len(base_o), "+ gauge words:", len(g_o), "=", len(merged))
    for c in checked:
        print("hook checked against the game program:", c)
    print("written:", out / NAME)
    print("sha1:", hashlib.sha1((out / NAME).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
