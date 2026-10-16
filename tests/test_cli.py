import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args, input=None):
        return subprocess.run([sys.executable, '-m', 'desktrace', *map(str, args)], input=input,
                              capture_output=True, text=True, encoding='utf8',
                              env=dict(os.environ, PYTHONIOENCODING='utf-8'), timeout=20)

    def test_normal_failure_invalid_and_unicode(self):
        s = {'version': 1, 'name': '中文测试', 'steps': [
            {'action': 'set_text', 'locator': {'automation_id': 'input', 'control_type': 'Edit'}, 'text': '中文 Ω'},
            {'action': 'assert_text', 'locator': {'automation_id': 'input', 'control_type': 'Edit'}, 'expected': '中文 Ω'}]}
        p = self.root / '脚本.json'
        p.write_text(json.dumps(s, ensure_ascii=False), encoding='utf8')
        good = self.cli('replay', p, '--backend', 'mock', '--runs', self.root)
        self.assertEqual(good.returncode, 0, good.stderr)
        result = json.loads(good.stdout)
        bundle = self.cli('verify', result['run_dir'])
        self.assertEqual(bundle.returncode, 0)
        s['steps'][-1]['expected'] = 'wrong'
        p.write_text(json.dumps(s), encoding='utf8')
        bad = self.cli('replay', p, '--backend', 'mock', '--runs', self.root)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(json.loads(bad.stdout)['status'], 'FAIL')
        p.write_text('{invalid', encoding='utf8')
        invalid = self.cli('replay', p, '--backend', 'mock')
        self.assertEqual(invalid.returncode, 1)
        self.assertEqual(json.loads(invalid.stderr)['error'], 'INVALID_JSON')

    def test_native_target_requires_explicit_authorization(self):
        p = self.cli('inspect', '--hwnd', 100, '--pid', 200)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(json.loads(p.stderr)['error'], 'AUTHORIZATION_REQUIRED')

    def test_record_json_lines_is_replayable(self):
        out = self.root / 'recorded.json'
        steps = [dict(action='set_text', locator=dict(automation_id='input', control_type='Edit'), text='public'),
                 dict(action='assert_text', locator=dict(automation_id='input', control_type='Edit'), expected='public')]
        p = self.cli('record', '--backend', 'mock', '--out', out, input='\n'.join(map(json.dumps, steps)))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(out.read_text(encoding='utf8'))['steps'], steps)


if __name__ == '__main__':
    unittest.main()
