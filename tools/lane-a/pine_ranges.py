"""Lane A: read memory ranges (and optionally the whole 32 MB) from a running sandbox emulator through PINE.

Waits for the session screenshot of each frame (p1_fNNNNNN.png) so the game has reached that frame, then reads.
Read-only.

  python -I tools/lane-a/pine_ranges.py <test-out-dir> <port> <frames> <ranges> [--full f1,f2] [--timeout 900]
     frames = 6500,6700,...      ranges = 0034D380:580,0038053E:2   (hex start : hex length)
Writes <outdir>/mem_f<frame>_<start>.bin and <outdir>/ram_f<frame>.bin.
"""
import pathlib
import socket
import struct
import sys
import time

RAM = 0x02000000


def recv_exact(s, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("PINE closed the connection")
        buf += chunk
    return bytes(buf)


def read(s, start, length):
    """Read [start, start+length) with read64 commands (start/length rounded to 8)."""
    a0 = start & ~7
    a1 = (start + length + 7) & ~7
    out = bytearray()
    addr = a0
    while addr < a1:
        n = min(50000, (a1 - addr) // 8)
        body = b"".join(b"\x03" + struct.pack("<I", addr + 8 * i) for i in range(n))
        s.sendall(struct.pack("<I", len(body) + 4) + body)
        size = struct.unpack("<I", recv_exact(s, 4))[0]
        reply = recv_exact(s, size - 4)
        if reply[0] != 0:
            raise RuntimeError(f"PINE refused a read at 0x{addr:08X}")
        out += reply[1:1 + 8 * n]
        addr += 8 * n
    off = start - a0
    return bytes(out[off:off + length])


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    ranges = [(int(r.split(":")[0], 16), int(r.split(":")[1], 16)) for r in sys.argv[4].split(",") if r]
    full = set()
    timeout = 900
    if "--full" in sys.argv:
        full = {int(x) for x in sys.argv[sys.argv.index("--full") + 1].split(",") if x}
    if "--timeout" in sys.argv:
        timeout = int(sys.argv[sys.argv.index("--timeout") + 1])
    t0 = time.time()
    for f in frames:
        shot = outdir / f"p1_f{f:06d}.png"
        while not shot.exists():
            if time.time() - t0 > timeout:
                sys.exit(f"timeout waiting for {shot.name}")
            time.sleep(0.02)
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=20) as s:
                for start, length in ranges:
                    (outdir / f"mem_f{f:06d}_{start:08X}.bin").write_bytes(read(s, start, length))
                if f in full:
                    (outdir / f"ram_f{f:06d}.bin").write_bytes(read(s, 0, RAM))
            print(f"frame {f}: ok" + (" (+full)" if f in full else ""))
        except Exception as e:  # noqa: BLE001
            print(f"frame {f}: read failed: {e}")


if __name__ == "__main__":
    main()
