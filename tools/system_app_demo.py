"""Real built-in Character Map E2E, no clipboard/button side effects or mock fallback."""
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
import uuid
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.adapters.windows import WindowsAdapter
from desktrace.engine import Recording, replay
from desktrace.model import load_script
from desktrace.report import write_json, verify_bundle
from private_desktop import PrivateDesktop


def main():
    out = ROOT / 'runs' / ('system-app-' + uuid.uuid4().hex); out.mkdir(parents=True)
    exe = Path(os.environ['WINDIR']) / 'System32/charmap.exe'
    summary = {'at': datetime.now(timezone.utc).isoformat(), 'kind': 'real-windows-system-app', 'application': 'Character Map',
               'directory': str(out), 'checks': {}, 'status': 'RUNNING'}
    write_json(out / 'plan.json', {'expected': ['fresh owned #32770 window', 'exact Unicode input/read', 'close/restart/replay pass',
                   'deliberate ASSERT_TEXT failure', 'actual target screenshot and verified bundles'],
                   'provider_contract': 'On the probed host Character Map TextPattern includes a final CR; the script expects that exact CR, with no core normalization',
                   'scope': 'System32/charmap.exe only on private desktop; no clipboard or button activation'})
    write_json(out / 'summary.json', summary)
    try:
        if not exe.is_file():
            summary.update(status='NOT RUN', reason='SYSTEM_CHARACTER_MAP_UNAVAILABLE')
        else:
            summary['executable_sha256'] = hashlib.sha256(exe.read_bytes()).hexdigest()
            script = load_script(ROOT / 'examples/charmap.json')
            with PrivateDesktop() as d:
                pid = d.launch(exe); w = d.wait_window(pid, class_prefix='#32770')
                a = WindowsAdapter(w['hwnd'], pid, desktop=d.name, allow_screenshot=True)
                controls = a.inspect(); write_json(out / 'controls.json', controls)
                if not any(c['locator'] == {'automation_id': '104', 'control_type': 'Edit'} and c['matches'] == 1 for c in controls):
                    raise RuntimeError('EXPECTED_SYSTEM_APP_CONTROL_NOT_EXPOSED')
                r = Recording(a, script['name'], runs=out / 'recording')
                for step in script['steps']: r.add(step)
                r.save(out / 'recorded.json');summary['checks']['record_unicode_read_assert'] = 'PASS'
                d.close_app(pid)
                closed = replay({'version': 1, 'name': 'Closed system app', 'steps': [dict(action='assert_window', state='exists', value=False)]}, a, out)
                summary['checks']['closed_window'] = closed['status']
                pid = d.launch(exe);w = d.wait_window(pid, class_prefix='#32770')
                a = WindowsAdapter(w['hwnd'],pid,desktop=d.name,allow_screenshot=True)
                good = replay(r.script,a,out);summary['checks']['fresh_process_replay'] = good['status'];summary['replay'] = good['run_dir']
                bad = copy.deepcopy(r.script);bad['steps'][1]['expected'] = 'Intentionally wrong'
                failure = replay(bad,a,out);summary['intentional_failure'] = failure['run_dir']
                summary['checks']['intentional_assertion_failure'] = 'PASS' if failure['status'] == 'FAIL' and failure['steps'][-1]['code'] == 'ASSERT_TEXT' else 'FAIL'
                summary['checks']['screenshot'] = failure['screenshot']['status']
                summary['checks']['manifest'] = 'PASS' if verify_bundle(Path(good['run_dir'])) and verify_bundle(Path(failure['run_dir'])) else 'FAIL'
            summary['status'] = 'PASS' if all(v == 'PASS' for v in summary['checks'].values()) else 'FAIL'
    except Exception as e:
        summary.update(status='FAIL', error_type=type(e).__name__, error=str(e))
        (out / 'traceback.txt').write_text(traceback.format_exc(),encoding='utf8')
    write_json(out / 'summary.json', summary);print(json.dumps(summary,ensure_ascii=True,indent=2))
    return 0 if summary['status'] in ('PASS','NOT RUN') else 1


if __name__ == '__main__':
    raise SystemExit(main())
