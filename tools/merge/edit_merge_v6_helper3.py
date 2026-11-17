"""One-off: experiment --helper2 in tools/merge/merge_v6.py: inside the twelfth glue, the helper in party place 2
thinks with the twin as the engine's player AND as party place 0."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "--helper2" in t:
    raise SystemExit("already there")
old = '''        code, labels = assemble(NEAR_AT, NEAR_SRC, {})'''
assert t.count(old) == 1
t = t.replace(old, '''        near_src = NEAR_SRC
        if "--helper2" in sys.argv:      # EXPERIMENT: the second helper is led by the twin (player pointer and party place 0)
            a0_, b0_ = "    beq t3,t2,nr_body             # a helper: unchanged", "    beq t3,t2,nr_helper"
            assert near_src.count(a0_) == 1
            near_src = near_src.replace(a0_, b0_) + """
nr_helper:
    lw t3,-31168(t5)              # 0x00348640: party place 2
    bne a0,t3,nr_body
    nop
    lw t3,0x48C(t6)
    beq t3,zero,nr_body
    nop
    lw t3,0(t3)
    beq t3,zero,nr_body           # the twin is down: the helper stays with player 1's hero
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t4,8(sp)
    lw t3,-31176(t5)              # 0x00348638: party place 0
    sd t3,16(sp)
    sw t6,-31176(t5)
    jal nr_body
    sw t6,-5816(t5)
    ld t4,8(sp)
    ld t3,16(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    sw t3,-31176(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""
        code, labels = assemble(NEAR_AT, near_src, {})''')
p.write_text(t, encoding="utf-8")
print("ok")
