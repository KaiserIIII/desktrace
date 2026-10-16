"""Owned test app lifecycle on a non-visible desktop. Not a security sandbox."""
import ctypes
from ctypes import wintypes as w
from pathlib import Path
import subprocess
import time
import uuid


class PrivateDesktop:
    def __init__(self):
        self.name = 'DeskTrace-' + uuid.uuid4().hex
        self.u = ctypes.WinDLL('user32', use_last_error=True)
        self.u.CreateDesktopW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.LPVOID, w.DWORD, w.DWORD, w.LPVOID]
        self.u.CreateDesktopW.restype = w.HANDLE
        self.u.CloseDesktop.argtypes = [w.HANDLE]
        self.handle = self.u.CreateDesktopW(self.name, None, None, 0, 0x00c3, None)
        if not self.handle:
            raise OSError(ctypes.get_last_error(), 'PRIVATE_DESKTOP_UNAVAILABLE')
        self.processes = []

    def launch(self, exe, args=()):
        import win32process
        si = win32process.STARTUPINFO()
        si.lpDesktop = self.name
        hp, ht, pid, tid = win32process.CreateProcess(str(Path(exe).resolve()),
              subprocess.list2cmdline([str(Path(exe).resolve()), *args]), None, None, False,
              0, None, str(Path(exe).resolve().parent), si)
        ht.Close()
        self.processes.append((hp, pid))
        return pid

    def wait_window(self, pid, timeout=15, class_prefix='WindowsForms10.Window.'):
        from desktrace.adapters.windows import list_windows
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rows = [r for r in list_windows(desktop=self.name)
                    if r['pid'] == pid and r['class_name'].startswith(class_prefix)]
            if len(rows) == 1:
                return rows[0]
            if len(rows) > 1:
                raise RuntimeError('MULTIPLE_OWNED_WINDOWS')
            time.sleep(.2)
        raise TimeoutError('OWNED_WINDOW_NOT_FOUND_ON_PRIVATE_DESKTOP')

    def close_app(self, pid):
        import win32api
        import win32event
        import win32process
        for hp, owned_pid in self.processes:
            if owned_pid == pid:
                # Only this launch's held process handle, never arbitrary PID or process name.
                if win32event.WaitForSingleObject(hp, 0) == 258:
                    win32api.TerminateProcess(hp, 0)
                win32event.WaitForSingleObject(hp, 5000)
                return
        raise ValueError('NOT_OWNED_PROCESS')

    def close(self):
        for hp, pid in self.processes:
            try: self.close_app(pid)
            finally: hp.Close()
        self.processes.clear()
        self.u.CloseDesktop(self.handle)

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
