"""Real Windows/UIA E2E. Saves attempts; no simulation fallback or desktop switch."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.adapters.windows import WindowsAdapter
from desktrace.engine import Recording, replay
from desktrace.report import verify_bundle, write_json
from private_desktop import PrivateDesktop


def main():
    out = ROOT / 'runs' / ('native-demo-' + uuid.uuid4().hex)
    out.mkdir(parents=True)
    summary = {'at': datetime.now(timezone.utc).isoformat(), 'kind': 'real-windows-uia', 'directory': str(out), 'checks': {}}
    write_json(out / 'summary.json', summary)
    try:
        csc = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        exe = out / 'DeskTraceFixture.exe'
        cmd = [str(csc), '/nologo', '/target:winexe', '/r:System.Windows.Forms.dll', '/r:System.Drawing.dll', '/out:' + str(exe), str(ROOT / 'tools/Fixture.cs')]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=30)
        write_json(out / 'compile.json', {'command': cmd, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
        if p.returncode: raise RuntimeError('FIXTURE_BUILD_FAILED')
        loc = {'automation_id': 'input', 'control_type': 'Edit'}
        output = {'automation_id': 'output', 'control_type': 'Edit'}
        steps = [dict(action='set_text', locator=loc, text='DeskTrace Unicode 中文 Ω'),
                 dict(action='assert_text', locator=loc, expected='DeskTrace Unicode 中文 Ω'),
                 dict(action='invoke', locator={'automation_id': 'apply', 'control_type': 'Button'}),
                 dict(action='assert_text', locator=output, expected='DeskTrace Unicode 中文 Ω'),
                 dict(action='assert_control', locator=loc, state='enabled', value=True),
                 dict(action='assert_window', state='normal', value=True)]
        with PrivateDesktop() as desktop:
            summary['private_desktop'] = desktop.name
            pid = desktop.launch(exe)
            window = desktop.wait_window(pid)
            write_json(out / 'selected_window.json', window)
            a = WindowsAdapter(window['hwnd'], pid, desktop=desktop.name, allow_screenshot=True)
            write_json(out / 'controls.json', a.inspect())
            rec = Recording(a, 'Real owned Windows fixture Unicode replay', runs=out / 'recording')
            for i, step in enumerate(steps):
                write_json(out / 'record_progress.json', {'step': i, 'action': step['action'], 'state': 'about_to_execute'})
                rec.add(step)
                write_json(out / 'record_progress.json', {'step': i, 'action': step['action'], 'state': 'executed'})
            rec.save(out / 'recorded.json')
            summary['checks']['record_and_verify'] = 'PASS'
            write_json(out / 'summary.json', summary)
            desktop.close_app(pid)
            closed = replay({'version': 1, 'name': 'Owned fixture closed', 'steps': [
                dict(action='assert_window', state='exists', value=False)]}, a, out)
            summary['checks']['closed_window_detected'] = closed['status']
            pid = desktop.launch(exe)
            window = desktop.wait_window(pid)
            a = WindowsAdapter(window['hwnd'], pid, desktop=desktop.name, allow_screenshot=True)
            good = replay(rec.script, a, out)
            summary['replay'] = good['run_dir']
            summary['checks']['restart_replay'] = good['status']
            bad_script = json.loads(json.dumps(rec.script))
            bad_script['steps'][-1] = dict(action='assert_text', locator=output, expected='Deliberately wrong')
            bad = replay(bad_script, a, out)
            summary['intentional_failure'] = bad['run_dir']
            summary['checks']['intentional_assertion_failure_detected'] = 'PASS' if bad['status'] == 'FAIL' and bad['steps'][-1]['code'] == 'ASSERT_TEXT' else 'FAIL'
            summary['checks']['real_failure_screenshot'] = bad['screenshot']['status']
            summary['checks']['evidence_manifest'] = 'PASS' if verify_bundle(Path(good['run_dir'])) and verify_bundle(Path(bad['run_dir'])) else 'FAIL'
            # Actual password-control and ambiguity probes on separately launched own fixtures.
            desktop.close_app(pid)
            for arg, code in [('--password-control', 'PASSWORD_CONTROL_BLOCKED'), ('--duplicate-control', 'AMBIGUOUS_LOCATOR')]:
                pid = desktop.launch(exe, [arg]); window = desktop.wait_window(pid)
                a = WindowsAdapter(window['hwnd'], pid, desktop=desktop.name, allow_screenshot=True)
                target = {'automation_id': 'password', 'control_type': 'Edit'} if arg == '--password-control' else loc
                result = replay({'version': 1, 'name': arg, 'steps': [dict(action='set_text', locator=target, text='Public test')]}, a, out)
                summary['checks'][arg] = 'PASS' if result['steps'][0]['code'] == code else 'FAIL'
                summary[arg] = result['run_dir']
                desktop.close_app(pid)
        summary['status'] = 'PASS' if all(s == 'PASS' for s in summary['checks'].values()) else 'FAIL'
    except Exception as e:
        summary['status'] = 'FAIL'
        summary['error_type'] = type(e).__name__
        summary['error'] = str(e)
        # Only our own public fixture is involved; keep full developer traceback for this controlled run.
        (out / 'traceback.txt').write_text(traceback.format_exc(), encoding='utf8')
    write_json(out / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
