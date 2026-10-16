"""Real Tk render/callback smoke on a private desktop, not a human usability test."""
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def child(desktop, fixture_hwnd, out):
    from desktrace.uia_worker import select_desktop
    select_desktop(desktop)
    import tkinter as tk
    from desktrace.gui import App
    from desktrace.adapters.windows import WindowsAdapter, list_windows
    from desktrace.report import write_json
    from desktrace.tk_runtime import configure_tk
    configure_tk()
    root = tk.Tk()
    app = App(root, desktop=desktop)
    summary = {'kind': 'real-tk-callback-smoke', 'checks': {}}
    def wait():
        deadline = time.monotonic() + 20
        while app.busy and time.monotonic() < deadline:
            root.update(); time.sleep(.02)
        root.update()
        if app.busy: raise TimeoutError('GUI_TASK_TIMEOUT')
    try:
        root.update()
        app.refresh(); wait()
        indices = [i for i, row in enumerate(app.windows) if row['hwnd'] == fixture_hwnd]
        assert len(indices) == 1
        app.window.current(indices[0]); app.consent.set(True); app.bind(); wait()
        assert app.adapter is not None
        summary['checks']['enumerate_select_bind'] = 'PASS'
        i = next(i for i, row in enumerate(app.controls) if row['locator'] == {'automation_id': 'input', 'control_type': 'Edit'})
        app.control.current(i); app.text.insert('1.0', 'GUI Unicode 中文 Ω')
        app.action.set('set_text'); app.record_step(); wait()
        app.action.set('assert_text'); app.record_step(); wait()
        script = json.loads(app.editor.get('1.0', 'end'))
        assert len(script['steps']) == 2, app.status.get()
        summary['checks']['gui_record_callbacks'] = 'PASS'
        app.recording.save(out / 'gui-recorded.json')
        app.replay_editor(); wait()
        assert app.status.get().startswith('PASS'), app.status.get()
        summary['checks']['gui_replay_callback'] = 'PASS'
        rows = [r for r in list_windows(desktop=desktop) if r['pid'] == __import__('os').getpid() and r['class_name'] == 'TkTopLevel']
        assert len(rows) == 1, rows
        a = WindowsAdapter(rows[0]['hwnd'], rows[0]['pid'], desktop=desktop, allow_screenshot=True)
        # Keep Tk pumping messages while another process queries this Tk provider.
        app.task(lambda: a.capture(out / 'gui.png'), lambda capture: summary.update(screenshot=capture))
        wait()
        assert summary.get('screenshot', {}).get('status') == 'PASS', app.status.get()
        summary['status'] = 'PASS'
    except Exception as e:
        summary.update(status='FAIL', error_type=type(e).__name__, error=str(e))
    finally:
        write_json(out / 'summary.json', summary)
        root.destroy()
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


def main():
    if len(sys.argv) == 5 and sys.argv[1] == '--child':
        return child(sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]))
    from private_desktop import PrivateDesktop
    out = ROOT / 'runs' / ('gui-smoke-' + uuid.uuid4().hex); out.mkdir(parents=True)
    # Reuse only our own successfully compiled fixture; no third-party executable.
    fixtures = sorted((ROOT / 'runs').glob('native-demo-*/DeskTraceFixture.exe'), key=lambda p: p.stat().st_mtime)
    with PrivateDesktop() as desktop:
        pid = desktop.launch(fixtures[-1]); window = desktop.wait_window(pid)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', desktop.name,
                            str(window['hwnd']), str(out)], capture_output=True, text=True, encoding='utf8', timeout=90)
        (out / 'stdout.log').write_text(p.stdout, encoding='utf8'); (out / 'stderr.log').write_text(p.stderr, encoding='utf8')
        print(p.stdout, p.stderr)
        return p.returncode


if __name__ == '__main__':
    raise SystemExit(main())
