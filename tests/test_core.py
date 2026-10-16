import copy
import json
from pathlib import Path
import tempfile
import unittest

from desktrace.model import DeskTraceError, validate_script
from desktrace.engine import Recording, replay
from desktrace.adapters.mock import MockAdapter
from desktrace.report import verify_bundle

LOC = {'automation_id': 'input', 'control_type': 'Edit'}


def script(*steps):
    return {'version': 1, 'name': 'public demo', 'steps': list(steps)}


class ContractTests(unittest.TestCase):
    def test_unicode_roundtrip(self):
        s = script({'action': 'set_text', 'locator': LOC, 'text': 'DeskTrace 中文 Ω'})
        self.assertEqual(validate_script(json.loads(json.dumps(s))), s)

    def test_unknown_action_and_unknown_fields_rejected(self):
        for s in (script({'action': 'shell', 'command': 'whoami'}),
                  dict(script(), hidden='secret'),
                  script({'action': 'invoke', 'locator': LOC, 'timeout': -1})):
            with self.subTest(s=s), self.assertRaises(DeskTraceError):
                validate_script(s)

    def test_no_unbounded_or_unscoped_locator(self):
        for loc in ({}, {'control_type': 'Edit'}, {'automation_id': 'input'}, {'index': 0}):
            with self.subTest(loc=loc), self.assertRaises(DeskTraceError):
                validate_script(script({'action': 'invoke', 'locator': loc}))

    def test_boolean_version_and_nonboolean_assertion_rejected(self):
        with self.assertRaises(DeskTraceError):
            validate_script({'version': True, 'name': 'x', 'steps': []})
        with self.assertRaises(DeskTraceError):
            validate_script(script({'action': 'assert_window', 'state': 'exists', 'value': 'false'}))

    def test_secret_like_test_data_rejected_before_execution(self):
        a = MockAdapter()
        with self.assertRaises(DeskTraceError):
            replay(script({'action': 'set_text', 'locator': LOC, 'text': 'password=hunter2'}), a, Path('unused'))
        self.assertEqual(a.calls, 0)

    def test_step_limit(self):
        with self.assertRaises(DeskTraceError):
            validate_script(script(*[{'action': 'assert_window', 'state': 'exists', 'value': True}] * 501))

    def test_non_string_action_and_state_have_contract_errors(self):
        for step in ({'action': []}, {'action': 'assert_window', 'state': [], 'value': True}):
            with self.subTest(step=step), self.assertRaises(DeskTraceError):
                validate_script(script(step))


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_record_execute_save_and_replay_on_fresh_adapter(self):
        r = Recording(MockAdapter(), 'recorded')
        for step in ({'action': 'set_text', 'locator': LOC, 'text': '测试 Ω'},
                     {'action': 'assert_text', 'locator': LOC, 'expected': '测试 Ω'}):
            r.add(step)
        p = self.root / 'script.json'
        r.save(p)
        result = replay(json.loads(p.read_text(encoding='utf8')), MockAdapter(), self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['backend'], 'mock')
        self.assertEqual(len(result['steps']), 2)

    def test_failed_recording_not_appended(self):
        r = Recording(MockAdapter(), 'x')
        with self.assertRaises(DeskTraceError):
            r.add({'action': 'assert_text', 'locator': LOC, 'expected': 'wrong'})
        self.assertEqual(r.script['steps'], [])

    def test_record_save_does_not_overwrite(self):
        r = Recording(MockAdapter(), 'x')
        p = self.root / 'x.json'
        r.save(p)
        with self.assertRaises(FileExistsError):
            r.save(p)

    def test_failed_recording_saves_evidence_without_retry(self):
        a = MockAdapter()
        r = Recording(a, 'audit', runs=self.root)
        with self.assertRaises(DeskTraceError) as cm:
            r.add({'action': 'assert_text', 'locator': LOC, 'expected': 'wrong'})
        self.assertEqual(a.calls, 1)
        self.assertEqual(r.script['steps'], [])
        self.assertTrue(verify_bundle(Path(cm.exception.evidence)))

    def test_empty_manifest_is_not_a_valid_run(self):
        run = self.root / 'empty'; run.mkdir()
        (run / 'manifest.json').write_text('{"algorithm":"sha256","files":{}}', encoding='utf8')
        self.assertFalse(verify_bundle(run))

    def test_failure_stops_and_saves_evidence(self):
        s = script({'action': 'assert_text', 'locator': LOC, 'expected': 'wrong'},
                   {'action': 'set_text', 'locator': LOC, 'text': 'never'})
        a = MockAdapter()
        result = replay(s, a, self.root)
        self.assertEqual((result['status'], result['failure_step'], a.calls), ('FAIL', 0, 1))
        self.assertEqual(result['steps'][0]['code'], 'ASSERT_TEXT')
        self.assertTrue((Path(result['run_dir']) / 'report.html').is_file())
        self.assertTrue(verify_bundle(Path(result['run_dir'])))

    def test_hash_manifest_detects_tampering(self):
        result = replay(script(), MockAdapter(), self.root)
        run = Path(result['run_dir'])
        (run / 'script.json').write_text('changed', encoding='utf8')
        self.assertFalse(verify_bundle(run))

    def test_ambiguous_locator_never_picks_first(self):
        a = MockAdapter(duplicate=True)
        result = replay(script({'action': 'set_text', 'locator': LOC, 'text': 'x'}), a, self.root)
        self.assertEqual(result['steps'][0]['code'], 'AMBIGUOUS_LOCATOR')
        self.assertEqual(a.controls[0]['text'], '')

    def test_missing_locator_diagnostic(self):
        loc = {'automation_id': 'missing', 'control_type': 'Edit'}
        result = replay(script({'action': 'invoke', 'locator': loc}), MockAdapter(), self.root)
        self.assertEqual(result['steps'][0]['code'], 'LOCATOR_NOT_FOUND')

    def test_password_control_never_read_or_written(self):
        for action in ('set_text', 'assert_text', 'invoke'):
            step = {'action': action, 'locator': {'automation_id': 'password', 'control_type': 'Edit'}}
            if action == 'set_text': step['text'] = 'public'
            if action == 'assert_text': step['expected'] = 'public'
            result = replay(script(step), MockAdapter(), self.root)
            self.assertEqual(result['steps'][0]['code'], 'PASSWORD_CONTROL_BLOCKED')

    def test_changed_window_is_not_rebound(self):
        result = replay(script({'action': 'assert_window', 'state': 'exists', 'value': True}), MockAdapter(changed=True), self.root)
        self.assertEqual(result['steps'][0]['code'], 'WINDOW_CHANGED')

    def test_window_and_control_assertions(self):
        s = script({'action': 'assert_window', 'state': 'normal', 'value': True},
                   {'action': 'assert_control', 'locator': LOC, 'state': 'enabled', 'value': True})
        self.assertEqual(replay(s, MockAdapter(), self.root)['status'], 'PASS')

    def test_logs_do_not_store_observed_text(self):
        a = MockAdapter()
        a.controls[0]['text'] = 'private-observed-string'
        result = replay(script({'action': 'assert_text', 'locator': LOC, 'expected': 'public'}), a, self.root)
        run = Path(result['run_dir'])
        for p in (run / 'result.json', run / 'events.jsonl', run / 'report.html'):
            self.assertNotIn('private-observed-string', p.read_text(encoding='utf8'))
        self.assertIn('sha256', (run / 'result.json').read_text(encoding='utf8'))

    def test_html_escapes_script_name(self):
        result = replay({'version': 1, 'name': '<img src=x onerror=alert(1)>', 'steps': []}, MockAdapter(), self.root)
        html = (Path(result['run_dir']) / 'report.html').read_text(encoding='utf8')
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;img', html)

    def test_runs_are_unique_and_screenshot_not_faked(self):
        a = replay(script(), MockAdapter(), self.root)
        b = replay(script({'action': 'assert_text', 'locator': LOC, 'expected': 'wrong'}), MockAdapter(), self.root)
        self.assertNotEqual(a['run_dir'], b['run_dir'])
        self.assertEqual(b['screenshot']['status'], 'NOT RUN')
        self.assertFalse(list(Path(b['run_dir']).glob('*.png')))

    def test_unexpected_adapter_error_is_redacted(self):
        class Broken(MockAdapter):
            def perform(self, step):
                raise RuntimeError('secret-exception-content')
        result = replay(script({'action': 'assert_window', 'state': 'exists', 'value': True}), Broken(), self.root)
        self.assertEqual(result['steps'][0]['code'], 'ADAPTER_ERROR')
        self.assertNotIn('secret-exception-content', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
