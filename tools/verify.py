"""Reproducible verification commands and full local logs, never fabricated results."""
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.report import write_json


def main():
    out = ROOT / 'runs' / ('verification-' + uuid.uuid4().hex); out.mkdir(parents=True)
    commands = []
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    def run(args, expected=0):
        p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, encoding='utf8', env=env, timeout=90)
        i = len(commands)
        (out / f'{i:02d}.stdout.log').write_text(p.stdout, encoding='utf8')
        (out / f'{i:02d}.stderr.log').write_text(p.stderr, encoding='utf8')
        row = {'argv': [sys.executable, *map(str, args)], 'cwd': str(ROOT), 'expected_exit': expected,
               'exit_code': p.returncode, 'status': 'PASS' if p.returncode == expected else 'FAIL',
               'stdout': f'{i:02d}.stdout.log', 'stderr': f'{i:02d}.stderr.log'}
        commands.append(row); write_json(out / 'commands.json', commands)
        return p
    tests = run(['-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    match = re.search(r'Ran (\d+) tests?', tests.stderr)
    run(['-m', 'pip', 'check'])
    run(['-m', 'desktrace', '--help'])
    good = run(['-m', 'desktrace', 'replay', 'examples/mock.json', '--backend', 'mock', '--runs', str(out)])
    if good.returncode == 0:
        result = json.loads(good.stdout)
        run(['-m', 'desktrace', 'verify', result['run_dir']])
    bad_script = json.loads((ROOT / 'examples/mock.json').read_text(encoding='utf8'))
    bad_script['steps'][1]['expected'] = 'Intentionally wrong'
    write_json(out / 'bad.json', bad_script)
    bad = run(['-m', 'desktrace', 'replay', str(out / 'bad.json'), '--backend', 'mock', '--runs', str(out)], expected=2)
    if good.returncode == 0 and bad.returncode == 2:
        good_dir, bad_dir = json.loads(good.stdout)['run_dir'], json.loads(bad.stdout)['run_dir']
        run(['-m', 'desktrace', 'compare', good_dir, bad_dir])
        run(['-m', 'desktrace', 'summarize', good_dir, good_dir])
    (out / 'invalid.json').write_text('{invalid', encoding='utf8')
    run(['-m', 'desktrace', 'replay', str(out / 'invalid.json'), '--backend', 'mock'], expected=1)
    run(['-m', 'desktrace', 'inspect', '--hwnd', '100', '--pid', '200'], expected=1)
    versions = {}
    for name in ['pywinauto', 'comtypes', 'pywin32', 'six', 'setuptools', 'pip']:
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name] = 'unavailable'
    summary = {'at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
               'platform': platform.platform(), 'versions': versions, 'test_count': int(match.group(1)) if match else None,
               'status': 'PASS' if all(x['status'] == 'PASS' for x in commands) else 'FAIL', 'directory': str(out), 'commands': commands}
    write_json(out / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
