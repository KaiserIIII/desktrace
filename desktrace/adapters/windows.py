"""Native operations run in disposable processes with a hard timeout."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
from ..model import DeskTraceError, validate_step


def worker_call(request, timeout=15):
    if sys.platform != 'win32':
        raise DeskTraceError('WINDOWS_REQUIRED')
    if not 0.1 <= timeout <= 60:
        raise DeskTraceError('INVALID_TIMEOUT')
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    try:
        p = subprocess.run([sys.executable, '-m', 'desktrace.uia_worker'], input=json.dumps(request),
                           capture_output=True, text=True, encoding='utf8', timeout=timeout, env=env,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        raise DeskTraceError('WORKER_TIMEOUT_OUTCOME_UNKNOWN') from None
    if p.returncode:
        raise DeskTraceError('WORKER_FAILED')
    try:
        response = json.loads(p.stdout)
        if type(response.get('ok')) is not bool or 'data' not in response:
            raise ValueError()
        if not response['ok']:
            code = response.get('code', 'UIA_ERROR')
            if not isinstance(code, str) or not code.replace('_', '').isalnum() or len(code) > 80:
                code = 'UIA_ERROR'
            raise DeskTraceError(code)
        if not isinstance(response['data'], (dict, list)):
            raise ValueError()
        return response['data']
    except (ValueError, AttributeError):
        raise DeskTraceError('INVALID_WORKER_RESPONSE') from None


class WindowsAdapter:
    kind = 'windows-uia'

    def __init__(self, hwnd, pid, *, timeout=15, desktop=None, allow_screenshot=False):
        self.timeout = timeout
        self.desktop = desktop
        self.allow_screenshot = allow_screenshot
        self.binding = worker_call({'operation': 'bind', 'hwnd': int(hwnd), 'pid': int(pid), 'desktop': desktop}, timeout)

    def environment(self):
        versions = {}
        for pkg in ('pywinauto', 'comtypes', 'pywin32', 'six'):
            try:
                versions[pkg] = importlib.metadata.version(pkg)
            except importlib.metadata.PackageNotFoundError:
                versions[pkg] = 'unavailable'
        return {'versions': versions, 'desktop': 'private' if self.desktop else 'current', 'binding': self.binding}

    def perform(self, step):
        validate_step(step)
        return worker_call({'operation': 'perform', 'desktop': self.desktop, 'binding': self.binding, 'step': step}, self.timeout)

    def inspect(self):
        return worker_call({'operation': 'inspect', 'desktop': self.desktop, 'binding': self.binding}, self.timeout)

    def capture(self, path):
        if not self.allow_screenshot:
            return {'status': 'NOT RUN', 'reason': 'SCREENSHOT_NOT_AUTHORIZED'}
        return worker_call({'operation': 'capture', 'desktop': self.desktop, 'binding': self.binding,
                            'path': str(Path(path).resolve())}, self.timeout)


def list_windows(*, desktop=None, include_titles=False):
    return worker_call({'operation': 'windows', 'desktop': desktop, 'include_titles': include_titles})
