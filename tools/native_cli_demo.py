"""Real CLI record/restart/replay/failure on our own private-desktop fixture."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.report import write_json
from private_desktop import PrivateDesktop


def main():
    out = ROOT / 'runs' / ('native-cli-' + uuid.uuid4().hex); out.mkdir(parents=True)
    fixtures = sorted((ROOT / 'runs').glob('native-demo-*/DeskTraceFixture.exe'), key=lambda p: p.stat().st_mtime)
    commands = []
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    def run(args, expected=0, input=None):
        argv = [sys.executable, '-m', 'desktrace', *map(str, args)]
        p = subprocess.run(argv, input=input, capture_output=True, text=True, encoding='utf8', env=env, timeout=90)
        n = len(commands);(out / f'{n}.stdout.log').write_text(p.stdout, encoding='utf8');(out / f'{n}.stderr.log').write_text(p.stderr, encoding='utf8')
        commands.append({'argv': argv, 'exit_code': p.returncode, 'expected_exit': expected,
                         'status': 'PASS' if p.returncode == expected else 'FAIL'})
        write_json(out / 'commands.json', commands)
        if p.returncode != expected: raise RuntimeError('CLI_UNEXPECTED_EXIT: ' + p.stderr)
        return json.loads(p.stdout)
    with PrivateDesktop() as d:
        pid = d.launch(fixtures[-1]); w = d.wait_window(pid)
        scope = ['--hwnd', w['hwnd'], '--pid', pid, '--desktop', d.name, '--authorize']
        rows = run(['windows', '--desktop', d.name])
        assert any(x['hwnd'] == w['hwnd'] for x in rows)
        run(['inspect', *scope])
        loc = {'automation_id': 'input', 'control_type': 'Edit'}
        steps = [dict(action='set_text', locator=loc, text='CLI 中文 Ω'), dict(action='assert_text', locator=loc, expected='CLI 中文 Ω')]
        jsonl = '\n'.join(json.dumps(s, ensure_ascii=False) for s in steps)
        script_path = out / '录制.json'; (out / 'record-input.jsonl').write_text(jsonl, encoding='utf8')
        run(['record', *scope, '--out', script_path, '--runs', out / 'recording'], input=jsonl)
        d.close_app(pid)
        pid = d.launch(fixtures[-1]); w = d.wait_window(pid)
        scope = ['--hwnd', w['hwnd'], '--pid', pid, '--desktop', d.name, '--authorize']
        good = run(['replay', script_path, *scope, '--runs', out])
        run(['verify', good['run_dir']])
        bad = json.loads(script_path.read_text(encoding='utf8')); bad['steps'][-1]['expected'] = 'Deliberately wrong'
        write_json(out / 'bad.json', bad)
        failure = run(['replay', out / 'bad.json', *scope, '--allow-screenshot', '--runs', out], expected=2)
        assert failure['steps'][-1]['code'] == 'ASSERT_TEXT' and failure['screenshot']['status'] == 'PASS'
        run(['verify', failure['run_dir']])
        summary = {'at': datetime.now(timezone.utc).isoformat(), 'kind': 'real-windows-uia-cli', 'status': 'PASS',
                   'directory': str(out), 'commands': commands, 'passing_replay': good['run_dir'], 'intentional_failure': failure['run_dir']}
        write_json(out / 'summary.json', summary); print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
