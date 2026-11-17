"""Dump the emulated PS2 main memory (32 MB) of a running sandbox emulator through PCSX2's PINE interface.

Waits for the session's screenshot of each given frame to appear (so we know the game has reached that frame),
then reads the whole memory and writes <outdir>/ram_f<frame>.bin. Read-only: it never writes to the game.

  python -I tools/pine_dump.py <test-out-dir> <port> <frame,frame,...> [--timeout 900]
"""
import pathlib
import socket
import struct
import sys
import time

RAM = 0x02000000
BATCH = 50000  # read64 commands per request (reply must stay under PINE's 450000-byte limit)


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
    with socket.create_connection(("127.0.0.1", port), timeout=20) as s:
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
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    timeout = 900
    if "--timeout" in sys.argv:
        timeout = int(sys.argv[sys.argv.index("--timeout") + 1])
    t0 = time.time()
    for f in frames:
        shot = outdir / f"p1_f{f:06d}.png"
        while not shot.exists():
            if time.time() - t0 > timeout:
                sys.exit(f"timeout waiting for {shot.name}")
            time.sleep(0.05)
        t1 = time.time()
        try:
            data = dump(port)
        except Exception as e:  # noqa: BLE001
            print(f"frame {f}: dump failed: {e}")
            continue
        (outdir / f"ram_f{f:06d}.bin").write_bytes(data)
        print(f"frame {f}: dumped {len(data)} bytes in {time.time() - t1:.1f} s")


if __name__ == "__main__":
    main()
