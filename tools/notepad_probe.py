"""One bounded system-app probe. Never attach a window outside the private desktop."""
import json
import os
from pathlib import Path
import sys
import time
import uuid
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.adapters.windows import list_windows
from desktrace.report import write_json
from private_desktop import PrivateDesktop


def main():
    out = ROOT / 'runs' / ('notepad-probe-' + uuid.uuid4().hex); out.mkdir(parents=True)
    with PrivateDesktop() as d:
        exe = Path(os.environ['WINDIR']) / 'System32/notepad.exe'
        pid = d.launch(exe)
        deadline = time.monotonic() + 10
        rows = []
        while time.monotonic() < deadline:
            rows = [r for r in list_windows(desktop=d.name) if r['pid'] == pid and r['class_name'] == 'Notepad']
            if rows: break
            time.sleep(.2)
        result = {'exe': str(exe), 'pid': pid, 'desktop': d.name, 'windows': rows,
                  'e2e_status': 'NOT RUN', 'reason': 'No system-app E2E is executed by this availability probe',
                  'availability': 'unique-owned-window' if len(rows) == 1 else 'no-unique-owned-window',
                  'command': [str(exe)], 'directory': str(out)}
        write_json(out / 'probe.json', result); print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
