"""Where does the memory of two linked emulator copies differ? (read-only, through PINE on both copies)

Waits until copy 1 has written the snapshot of the given frame, then reads the whole PS2 main memory of copy 1,
then copy 2, then copy 1 again. Addresses that changed between the two reads of copy 1 are "moving" (timers,
animation); addresses where copy 2 differs from BOTH reads of copy 1 and that are not moving are reported as
real differences, grouped into ranges.

  python -I tools/lane-v3/dump2.py <test-out-dir> <port1> <port2> <frame> [--timeout 600]
"""
import pathlib
import socket
import struct
import sys
import time

RAM = 0x02000000
BATCH = 50000


def recv_exact(s, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("PINE closed the connection")
        buf += chunk
    return bytes(buf)


def dump(port):
    out = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=30) as s:
        addr = 0
        while addr < RAM:
            n = min(BATCH, (RAM - addr) // 8)
            body = b"".join(b"\x03" + struct.pack("<I", addr + 8 * i) for i in range(n))
            s.sendall(struct.pack("<I", len(body) + 4) + body)
            size = struct.unpack("<I", recv_exact(s, 4))[0]
            reply = recv_exact(s, size - 4)
            if reply[0] != 0:
                raise RuntimeError(f"PINE refused a read at 0x{addr:08X}")
            out += reply[1:1 + 8 * n]
            addr += 8 * n
    return bytes(out)


def main():
    outdir = pathlib.Path(sys.argv[1])
    p1, p2, frame = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
    shot = outdir / f"p1_f{frame:06d}.png"
    t0 = time.time()
    while not shot.exists():
        if time.time() - t0 > timeout:
            sys.exit("timeout waiting for " + shot.name)
        time.sleep(0.05)
    a1 = dump(p1)
    b = dump(p2)
    a2 = dump(p1)
    n = len(a1)
    xa = (int.from_bytes(a1, "little") ^ int.from_bytes(a2, "little")).to_bytes(n, "little")
    x1 = (int.from_bytes(a1, "little") ^ int.from_bytes(b, "little")).to_bytes(n, "little")
    x2 = (int.from_bytes(a2, "little") ^ int.from_bytes(b, "little")).to_bytes(n, "little")
    moving = sum(1 for i in range(0, n, 4) if xa[i:i + 4] != b"\0\0\0\0")
    real = [i for i in range(0, n, 4)
            if x1[i:i + 4] != b"\0\0\0\0" and x2[i:i + 4] != b"\0\0\0\0" and xa[i:i + 4] == b"\0\0\0\0"]
    # group into ranges (gaps up to 64 bytes are joined)
    ranges = []
    for i in real:
        if ranges and i - ranges[-1][1] <= 64:
            ranges[-1][1] = i + 4
            ranges[-1][2] += 1
        else:
            ranges.append([i, i + 4, 1])
    lines = [f"frame {frame}: words moving inside copy 1 between its two reads: {moving}",
             f"words where copy 2 differs from copy 1 (not moving): {len(real)} in {len(ranges)} range(s)"]
    for r in sorted(ranges, key=lambda r: -r[2])[:40]:
        lines.append(f"  0x{r[0]:08X}-0x{r[1]:08X}  {r[2]} words differ of {(r[1] - r[0]) // 4}")
    (outdir / f"memdiff_f{frame:06d}.txt").write_text("\n".join(lines) + "\n")
    (outdir / f"ram_p1_f{frame:06d}.bin").write_bytes(a1)
    (outdir / f"ram_p2_f{frame:06d}.bin").write_bytes(b)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
