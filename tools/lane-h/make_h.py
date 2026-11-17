"""Lane H patch generator: enemies choose between BOTH heroes (CRC F266B00B, KH2 Final Mix SLPM-66675).

  python -I tools/lane-h/make_h.py <outDir> [options]

The output = every line of the merged build v2 (patches/merged-v2, read as it is) + this lane's section.
Options (each adds one part; default = "search" only):
  --khi N.NN      "clearly closer" factor (default 1.5): if one hero is more than KHI times closer, the enemy takes it
  --klo N.NN      "about as close" factor (default 1.25): if neither is more than KLO times closer, the two heroes
                  share the enemy in turns; between KLO and KHI the enemy keeps the hero it already targets
  --epoch N       length of a turn as a power of two of video frames (default 9: 512 frames, about 8.5 s)
  --no-search     leave the target-search part out (for control runs of the other parts)
  --player-trap   also make the AI script call "get the player" return the calling object's own chosen hero
  --base DIR      base patch folder (default patches/merged-v2)
  --debug         TEST BUILDS ONLY: count at 0x000F27D0.. how often each path runs (searches decided by the rule,
                  "get the player" answered with the twin / decided by the rule / with player 1's hero)

Writes SLPM-66675_F266B00B.pnach and listing.txt (every word of this lane with its meaning, hook sites with the
original instruction). Code cave of this lane: 0x000F2000-0x000F27FF.
"""
import hashlib
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from asm import assemble  # noqa: E402
import mips  # noqa: E402

ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"
CAVE_LO, CAVE_HI = 0x000F2000, 0x000F2800

SYM = {
    "G_PLAYER": 0x0034E948,     # engine's player object pointer (player 1's hero in the merged build)
    "V_TWIN": 0x000F05CC,       # lane E: the twin object, 0 if none
    "SET_TARGET": 0x00190878,   # game: target record a0 = object a1, part a2
    "POS_OF": 0x0016C028,       # game: pointer to an object's position vector
    "VM_ROOT": 0x0034D8A0,      # game: script context that is running now (0 outside scripts)
    "G_FRAME": 0x0034D4BC,      # game: frame counter (one per video frame)
    "H_VARS": 0x000F27C0,       # this lane's variables (zero at boot)
    "H_CNT": 0x000F27D0,        # test builds (--debug) only: four counters
}

# ---------------------------------------------------------------------------------------------------------------
# h_choose: the rule.  in: s0 = the searching object, t7 = player 1's hero, t6 = the twin, t5 = the searcher's
# previous target object (or 0).  out: v0 = the hero to target.  Uses only game state.
# ---------------------------------------------------------------------------------------------------------------
SEARCH = """
h_tail:                             # reached instead of 'SET_TARGET(record a0, object a1, part a2)' at the end of the
                                    # target search modes 0, 1, 2.  s0 = the searching object (dispatcher's s0)
    lui   t7,%hi(G_PLAYER)
    lw    t7,%lo(G_PLAYER)(t7)      # player 1's hero
    bne   a1,t7,h_pass              # the search did not end on "the player" (decoy list or last attacker): keep it
    lui   t6,%hi(V_TWIN)
    lw    t6,%lo(V_TWIN)(t6)
    beq   t6,zero,h_pass            # no twin in this room: the game's own behaviour
    nop
    beq   s0,zero,h_pass
    nop
    addiu sp,sp,-48
    sd    ra,0(sp)
    sd    a0,8(sp)
    sd    a2,16(sp)
    sd    s1,24(sp)
    sd    s2,32(sp)
@dbg lui   t4,%hi(H_CNT)
@dbg lw    t3,%lo(H_CNT)(t4)
@dbg addiu t3,t3,1
@dbg sw    t3,%lo(H_CNT)(t4)        # test builds only: count the searches decided by the rule
    jal   h_choose
    lw    t5,0(a0)                  # the searcher's previous target
    move  a1,v0
    ld    ra,0(sp)
    ld    a0,8(sp)
    ld    a2,16(sp)
    ld    s1,24(sp)
    ld    s2,32(sp)
    addiu sp,sp,48
h_pass:
    j     SET_TARGET
    nop

h_choose:                           # s0 = searcher, t7 = hero, t6 = twin, t5 = previous target; returns v0
    addiu sp,sp,-32
    sd    ra,0(sp)
    sd    s3,8(sp)
    move  s1,t7
    move  s2,t6
    move  s3,t5
    lw    t0,0x48C(s1)              # hero's unit slot
    lw    t1,0x48C(s2)              # twin's unit slot
    beq   t0,zero,h_ret_hero
    nop
    beq   t1,zero,h_ret_hero
    nop
    lw    t0,0(t0)                  # hero's HP
    lw    t1,0(t1)                  # twin's HP
    blez  t1,h_ret_hero             # the twin is down: player 1's hero
    nop
    blez  t0,h_ret_twin             # the hero is down: the twin
    nop
    jal   POS_OF
    move  a0,s0
    lwc1  f0,0(v0)
    lwc1  f1,4(v0)
    lwc1  f2,8(v0)
    jal   POS_OF
    move  a0,s1
    lwc1  f3,0(v0)
    lwc1  f4,4(v0)
    lwc1  f5,8(v0)
    sub.s f3,f3,f0
    sub.s f4,f4,f1
    sub.s f5,f5,f2
    mul.s f3,f3,f3
    mul.s f4,f4,f4
    mul.s f5,f5,f5
    add.s f3,f3,f4
    add.s f8,f3,f5                  # f8 = squared distance searcher - hero
    jal   POS_OF
    move  a0,s2
    lwc1  f3,0(v0)
    lwc1  f4,4(v0)
    lwc1  f5,8(v0)
    sub.s f3,f3,f0
    sub.s f4,f4,f1
    sub.s f5,f5,f2
    mul.s f3,f3,f3
    mul.s f4,f4,f4
    mul.s f5,f5,f5
    add.s f3,f3,f4
    add.s f9,f3,f5                  # f9 = squared distance searcher - twin
    c.lt.s f9,f8
    bc1t  h_twin_near
    nop
    move  t0,s1                     # t0 = the nearer hero (a tie: player 1's hero), t1 = the farther one
    move  t1,s2
    mov.s f10,f8                    # f10 = nearer squared distance, f11 = farther
    b     h_cmp
    mov.s f11,f9
h_twin_near:
    move  t0,s2
    move  t1,s1
    mov.s f10,f9
    mov.s f11,f8
h_cmp:
    lui   t2,KHI_HI
    ori   t2,t2,KHI_LO
    mtc1  t2,f6                     # f6 = KHI * KHI
    mul.s f7,f10,f6
    c.lt.s f7,f11                   # farther > KHI * nearer: one hero is clearly closer
    bc1t  h_ret
    move  v0,t0                     #   -> the nearer hero
    lui   t2,KLO_HI
    ori   t2,t2,KLO_LO
    mtc1  t2,f6                     # f6 = KLO * KLO
    mul.s f7,f10,f6
    c.lt.s f11,f7                   # farther < KLO * nearer: both about as close
    bc1t  h_share
    nop
    beq   s3,s1,h_ret_hero          # in between: keep the hero it already targets ...
    nop
    beq   s3,s2,h_ret_twin
    nop
    b     h_ret                     # ... or take the nearer one
    move  v0,t0
h_share:                            # both about as close: this enemy's turn alternates with time
    lui   t2,%hi(G_FRAME)
    lw    t2,%lo(G_FRAME)(t2)       # the game's frame counter
    srl   t3,s0,4                   # each enemy has its own phase (from its address)
    addu  t2,t2,t3
    srl   t2,t2,EPOCH
    andi  t2,t2,1
    bne   t2,zero,h_ret_twin
    nop
h_ret_hero:
    b     h_ret
    move  v0,s1
h_ret_twin:
    move  v0,s2
h_ret:
    ld    ra,0(sp)
    ld    s3,8(sp)
    jr    ra
    addiu sp,sp,32
"""

HOOKS_SEARCH = [
    # address, new word maker, original word, meaning
    (0x00190A74, "j", "h_tail", 0x0806421E, "target search mode 0 (decoy list, else the player): end goes through the rule"),
    (0x00190B28, "j", "h_tail", 0x0806421E, "target search mode 1 (decoy list, the object remembered at object+0xAEC, else the player): same"),
    (0x001909A8, "jal", "h_tail", 0x0C06421E, "target search mode 2 (the player): same"),
]


def jword(kind, target):
    return ((2 if kind == "j" else 3) << 26) | ((target >> 2) & 0x3FFFFFF)


def elf_word_reader():
    e = mips.Elf(str(ELF))
    va, off, fs = e.segs[0]

    def word(addr):
        if va <= addr < va + fs:
            return struct.unpack_from("<I", e.data, off + addr - va)[0]
        return None
    return word


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    out = pathlib.Path(args[0])
    khi, klo, epoch = 1.5, 1.25, 9
    base_dir = ROOT / "patches" / "merged-v2"
    if "--khi" in args:
        khi = float(args[args.index("--khi") + 1])
    if "--klo" in args:
        klo = float(args[args.index("--klo") + 1])
    if "--epoch" in args:
        epoch = int(args[args.index("--epoch") + 1])
    if "--base" in args:
        base_dir = pathlib.Path(args[args.index("--base") + 1])
    use_search = "--no-search" not in args
    use_ptrap = "--player-trap" in args

    base_file = base_dir / "SLPM-66675_F266B00B.pnach"
    base_text = base_file.read_text()
    base_sha = hashlib.sha1(base_file.read_bytes()).hexdigest()
    base_words = {}
    for line in base_text.splitlines():
        if line.startswith("patch=1,EE,"):
            p = line.split(",")
            base_words[int(p[2], 16)] = int(p[4], 16)

    kh = struct.unpack("<I", struct.pack("<f", khi * khi))[0]
    kl = struct.unpack("<I", struct.pack("<f", klo * klo))[0]
    sym = dict(SYM)
    sym.update({"KHI_HI": kh >> 16, "KHI_LO": kh & 0xFFFF, "KLO_HI": kl >> 16, "KLO_LO": kl & 0xFFFF, "EPOCH": epoch})

    src = ""
    hooks = []
    if use_search:
        src += SEARCH
        hooks += HOOKS_SEARCH
    if use_ptrap:
        import h_ptrap
        src += h_ptrap.SOURCE
        hooks += h_ptrap.HOOKS
        sym.update(h_ptrap.SYM)
    debug = "--debug" in args
    nl = chr(10)
    src = nl.join((l.replace("@dbg", "    ", 1) if debug else "") if l.lstrip().startswith("@dbg") else l
                  for l in src.split(nl))
    words, labels = assemble(CAVE_LO, src, sym)
    if CAVE_LO + 4 * len(words) > sym["H_VARS"]:
        sys.exit("code does not fit below the variables")
    word = elf_word_reader()

    code = {CAVE_LO + 4 * i: w for i, w in enumerate(words)}
    hook_words, problems = {}, []
    for addr, kind, target, orig, meaning in hooks:
        if kind in ("j", "jal"):
            w = jword(kind, labels[target])
        else:
            w = int(target)
        have = word(addr)
        if have != orig:
            problems.append("hook %08X: program has %s, expected %08X" % (addr, "%08X" % have if have is not None else "?", orig))
        if addr in base_words:
            problems.append("hook %08X is already written by the base patch" % addr)
        hook_words[addr] = (w, orig, meaning)
    for a in code:
        if a in base_words:
            problems.append("code address %08X is used by the base patch" % a)
        if word(a) is not None:
            problems.append("code address %08X is inside the program file" % a)
    if problems:
        sys.exit("PROBLEMS:\n  " + "\n  ".join(problems))

    out.mkdir(parents=True, exist_ok=True)
    parts = [p for p, on in (("target search", use_search), ("player trap", use_ptrap)) if on]
    lines = [l for l in base_text.splitlines() if l.strip()]
    lines.append("comment=Lane H (enemies choose between both heroes: %s; KHI=%.2f KLO=%.2f turn=2^%d frames), made by tools/lane-h/make_h.py on top of the lines above." % (
        ", ".join(parts), khi, klo, epoch))
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hook_words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hook_words[a][0]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")

    rev = {}
    for name, addr in labels.items():
        if CAVE_LO <= addr < CAVE_HI:
            rev.setdefault(addr, []).append(name)
    lst = ["Lane H patch for CRC F266B00B: the lines of %s (SHA-1 %s, %d words) plus the words below." % (
        base_file.relative_to(ROOT), base_sha, len(base_words)),
        "Parts: %s. KHI = %.2f (KHI*KHI = %08X as a float), KLO = %.2f (%08X), turn length 2^%d video frames." % (
            ", ".join(parts), khi, kh, klo, kl, epoch), "",
        "ROUTINES (cave 0x%08X-0x%08X, %d words)" % (CAVE_LO, CAVE_LO + 4 * len(words) - 1, len(words))]
    src_lines = [l for l in src.split("\n") if l.split("#", 1)[0].strip() and not l.split("#", 1)[0].strip().endswith(":")]
    for i, w in enumerate(words):
        a = CAVE_LO + 4 * i
        for n in rev.get(a, []):
            lst.append("%s:" % n)
        comment = src_lines[i].split("#", 1)[1].strip() if "#" in src_lines[i] else ""
        lst.append("  %08X  %08X  %-34s%s" % (a, w, mips.dis(w, a), ("# " + comment) if comment else ""))
    lst += ["", "HOOKS (words changed inside the game program; none is used by the merged build v2)"]
    for a in sorted(hook_words):
        w, orig, meaning = hook_words[a]
        lst.append("  %08X  %08X  %-24s was %08X %-26s %s" % (a, w, mips.dis(w, a), orig, mips.dis(orig, a), meaning))
    if use_ptrap or debug:
        lst += ["", "VARIABLES of this lane (not written by the patch file; they rely on zero memory at boot): 0x%08X-0x%08X" % (
            sym["H_VARS"], CAVE_HI - 1)]
    else:
        lst += ["", "VARIABLES: none. This patch keeps no data of its own (it reads lane E's twin pointer 0x000F05CC)."]
    (out / "listing.txt").write_text("\n".join(lst) + "\n")
    print("base %d words (%s) + lane H %d code words + %d hook words -> %s" % (
        len(base_words), base_sha[:10], len(code), len(hook_words), out / "SLPM-66675_F266B00B.pnach"))


if __name__ == "__main__":
    main()
