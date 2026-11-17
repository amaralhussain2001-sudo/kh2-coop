import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/nprobe.py")
s = p.read_text(encoding="utf-8")
old = """            fr, _, n = fr.partition("+")
            tps.append([who, tgt, int(fr), int(n) if n else 12, False])"""
new = """            fr, _, n = fr.partition("+")
            n, _, dx = n.partition(":")
            tps.append([who, tgt, int(fr), int(n) if n else 12, False, float(dx) if dx else 60.0])"""
assert old in s
s = s.replace(old, new)
old = """                                p.wf(byrole[t[0]] + off, x + 60.0)"""
new = """                                p.wf(byrole[t[0]] + off, x + t[5])"""
assert old in s
s = s.replace(old, new)
old = "x + 60, y, z))"
new = "x + t[5], y, z))"
assert old in s, "fmt"
s = s.replace(old, new)
old = """                        byrole = {u["role"]: u["owner"] for u in us}"""
new = """                        byrole = {u["role"]: u["owner"] for u in us}
                        byrole.update({"sid%d" % u["sid"]: u["owner"] for u in us if u["role"].startswith("sid")})"""
assert old in s
s = s.replace(old, new)
s = s.replace("# --tp WHO>TARGET@FRAME[+N]: for N samples (default 6) write WHO's position = TARGET's + 60 units in x",
              "# --tp WHO>TARGET@FRAME[+N[:DX]]: for N samples write WHO's position = TARGET's + DX units in x (default 60)")
p.write_text(s, encoding="utf-8")
print("ok")
