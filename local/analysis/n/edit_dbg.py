import sys, pathlib
p = pathlib.Path(sys.argv[1]); t = p.read_text(encoding="utf-8")
old = """n_hp:                             # a0 = player object, a1 = HP change, a2 = gauge (0 = HP), a3 = flag
    blez a1,n_hp_orig             # only a heal can bring a hero back
    nop
"""
new = old + "@DEBUG@\n"
assert old in t and "@DEBUG@" not in t
t = t.replace(old, new, 1)
old = """    elf = mips.Elf(str(ELF))
    words, syms = assemble(CAVE, SRC, SYM)
"""
new = """    dbg = ""
    if "--debug" in args:      # TEST ONLY: remember who healed a player object last (return addresses, amount, object)
        dbg = ("    lui t7,%hi(N_DBG)\n    sw ra,%lo(N_DBG)(t7)\n    ld t6,0(sp)\n    sw t6,%lo(N_DBG4)(t7)\n"
               "    sw a1,%lo(N_DBG8)(t7)\n    sw a0,%lo(N_DBGC)(t7)\n")
        SYM.update(N_DBG=0x000F2FE0, N_DBG4=0x000F2FE4, N_DBG8=0x000F2FE8, N_DBGC=0x000F2FEC)
    elf = mips.Elf(str(ELF))
    words, syms = assemble(CAVE, SRC.replace("@DEBUG@\n", dbg), SYM)
"""
assert old in t
t = t.replace(old, new, 1)
p.write_text(t, encoding="utf-8"); print("ok")
