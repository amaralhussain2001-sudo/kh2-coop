"""Start test emulators on a SEPARATE, HIDDEN Windows desktop, so their windows can never take the keyboard focus
from whatever the user is doing (user request 2026-11-10: tests must not disturb a game being played).

A Windows "desktop" here is the system object (CreateDesktop), not a virtual desktop of the task bar: windows made
on it are not on the user's screen at all, are not in the task bar and cannot become the active window there.
The emulator still runs and draws normally (the test pictures come from the emulator's own picture buffers, not
from the screen).

  from quiet_launch import popen, ENABLED
  p = popen([exe, arg, ...], env=dict, cwd=str, stdout=open_file)   ->  object with pid, poll(), kill(), wait(),
                                                                         returncode (like subprocess.Popen)

Switch it off with the environment variable KH2_TEST_DESKTOP=0 (the tests then use the normal desktop again).
"""
import ctypes
import msvcrt
import os
import subprocess
from ctypes import wintypes

# KH2_TEST_SHOW=1 (user request 2026-11-13, "run it in front of me"): the test emulators start on the user's OWN
# desktop, stay on screen and are put side by side (player 1 left, player 2 right). It switches the hidden
# desktop off by itself.
SHOW = os.environ.get("KH2_TEST_SHOW", "0") == "1"
ENABLED = os.environ.get("KH2_TEST_DESKTOP", "1") != "0" and not SHOW
DESKTOP_NAME = "kh2-test-desktop"

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

GENERIC_ALL = 0x10000000
STARTF_USESTDHANDLES = 0x00000100
CREATE_UNICODE_ENVIRONMENT = 0x00000400
WAIT_OBJECT_0 = 0
STILL_ACTIVE = 259


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR), ("lpDesktop", wintypes.LPWSTR),
                ("lpTitle", wintypes.LPWSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD),
                ("dwYCountChars", wintypes.DWORD), ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD), ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD),
                ("dwThreadId", wintypes.DWORD)]


user32.CreateDesktopW.restype = wintypes.HANDLE
user32.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD,
                                  wintypes.DWORD, ctypes.c_void_p]
kernel32.CreateProcessW.restype = wintypes.BOOL
kernel32.CreateProcessW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
                                    wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
                                    ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION)]
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

_desktop_handle = None


def _desktop():
    """Create the hidden desktop (or open it if another test made it). The handle stays open while we live."""
    global _desktop_handle
    if _desktop_handle is None:
        h = user32.CreateDesktopW(DESKTOP_NAME, None, None, 0, GENERIC_ALL, None)
        if not h:
            raise OSError(ctypes.get_last_error(), "CreateDesktop failed")
        _desktop_handle = h
    return _desktop_handle


class QuietProcess:
    def __init__(self, handle, pid):
        self._h = handle
        self.pid = pid
        self.returncode = None

    def poll(self):
        if self.returncode is None and kernel32.WaitForSingleObject(self._h, 0) == WAIT_OBJECT_0:
            code = wintypes.DWORD()
            kernel32.GetExitCodeProcess(self._h, ctypes.byref(code))
            self.returncode = ctypes.c_int32(code.value).value
        return self.returncode

    def wait(self, timeout=None):
        ms = 0xFFFFFFFF if timeout is None else int(timeout * 1000)
        kernel32.WaitForSingleObject(self._h, ms)
        return self.poll()

    def kill(self):
        if self.poll() is None:
            kernel32.TerminateProcess(self._h, 1)
            kernel32.WaitForSingleObject(self._h, 5000)
            self.poll()


def popen(cmd, env=None, cwd=None, stdout=None):
    """Like subprocess.Popen(cmd, env=env, cwd=cwd, stdout=stdout, stderr=STDOUT), on the hidden desktop."""
    if not ENABLED:
        return subprocess.Popen(cmd, env=env, cwd=cwd, stdout=stdout, stderr=subprocess.STDOUT if stdout else None)
    _desktop()
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = "WinSta0\\" + DESKTOP_NAME
    inherit = False
    if stdout is not None:
        h = msvcrt.get_osfhandle(stdout.fileno())
        os.set_handle_inheritable(h, True)
        si.dwFlags |= STARTF_USESTDHANDLES
        si.hStdOutput = h
        si.hStdError = h
        si.hStdInput = None
        inherit = True
    env_block = None
    if env is not None:
        text = "".join("%s=%s\0" % (k, v) for k, v in sorted(env.items(), key=lambda kv: kv[0].upper())) + "\0"
        env_block = ctypes.create_unicode_buffer(text, len(text))
    cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline([str(c) for c in cmd]))
    pi = PROCESS_INFORMATION()
    ok = kernel32.CreateProcessW(None, cmdline, None, None, inherit, CREATE_UNICODE_ENVIRONMENT, env_block,
                                 str(cwd) if cwd else None, ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        raise OSError(ctypes.get_last_error(), "CreateProcess failed for %s" % cmd[0])
    kernel32.CloseHandle(pi.hThread)
    return QuietProcess(pi.hProcess, pi.dwProcessId)


def place(pid, index, seconds=40.0):
    """SHOW mode: put the windows of process <pid> into slot <index> (0 = left half, 1 = right half of the main
    screen) without giving them the keyboard focus. Call it in a thread; it watches for <seconds>."""
    import time
    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    w = min(sw // 2, 1000)
    h = min(sh - 80, w * 3 // 4 + 60)
    x = (sw // 2 - w) if index == 0 else sw // 2
    y = max(0, (sh - h) // 3)
    done = set()

    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and user32.IsWindowVisible(hwnd) and hwnd not in done:
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 4)          # SW_SHOWNOACTIVATE
            user32.SetWindowPos(hwnd, None, x, y, w, h, 0x0010 | 0x0004)   # SWP_NOACTIVATE | SWP_NOZORDER
            done.add(hwnd)
        return True

    end = time.time() + seconds
    while time.time() < end:
        try:
            user32.EnumWindows(proto(cb), 0)
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.3)
