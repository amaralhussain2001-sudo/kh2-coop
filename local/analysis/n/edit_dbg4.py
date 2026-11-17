import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
rep('''"    sw t3,44(t7)", "    lw t3,0(a0)", "    sw t3,48(t7)", "    sw ra,52(t7)",
                             "    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,56(t7)", ""])''',
    '''"    sw t3,44(t7)", "    lw t3,0(a0)", "    sw t3,48(t7)",
                             "    lui t3,0x0035", "    lw t4,-0x2760(t3)", "    sw t4,52(t7)",      # 0x0034D8A0 root thread
                             "    lw t4,-0x275C(t3)", "    sw t4,56(t7)",                            # 0x0034D8A4 this thread
                             "    lui t3,%hi(G_PLAYER)", "    lw t3,%lo(G_PLAYER)(t3)", "    lw t3,0x484(t3)", "    sw t3,60(t7)",
                             "    lui t3,%hi(V_TWIN)", "    lw t3,%lo(V_TWIN)(t3)", "    lw t3,0x484(t3)", "    sw t3,28(t7)", ""])''')
rep('''"    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,28(t7)",
                             "    sw ra,32(t7)",''', '''"    sw ra,32(t7)",''')
p.write_text(s, encoding="utf-8")

p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/nprobe.py")
s = p.read_text(encoding="utf-8")
rep("""                ex = " ".join("%08X=%08X" % (a, p.r32(a)) for a in extra)""",
    """                ex = " ".join("%08X=%08X" % (a, p.r32(a)) for a in extra)
                if "--thread" in sys.argv:   # read-only: dump the script thread the debug patch saw last (0x000F2FB4, 0x000F2FB8)
                    for ta in (0x000F2FB4, 0x000F2FB8):
                        tv = p.r32(ta)
                        if tv and tv != seen_thr.get(ta):
                            seen_thr[ta] = tv
                            fh.write("%6d  THREAD at %08X = %08X: %s" % (f, ta, tv, " ".join("%08X" % w for w in struct.unpack("<24I", p.read(tv, 96)))) + chr(10))""")
rep("""    want_att, seen_att = "--attacks" in sys.argv, set()""", """    want_att, seen_att = "--attacks" in sys.argv, set()
    seen_thr = {}""")
p.write_text(s, encoding="utf-8")
print("ok")
