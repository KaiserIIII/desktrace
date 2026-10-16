import copy
import unittest
from desktrace.analysis import compare_results, summarize_repeats, minimize


def result(status='PASS', observation=None, step_hash='assertion'):
    return {'status': status, 'backend': 'mock', 'failure_step': None if status == 'PASS' else 0,
            'steps': [{'action': 'assert_text', 'status': status, 'code': 'OK' if status == 'PASS' else 'ASSERT_TEXT',
                       'step_sha256': step_hash, 'observed': observation or {'text': {'sha256': 'abc', 'length': 3}}}]}


class AnalysisTests(unittest.TestCase):
    def test_compare_ignores_runtime_but_detects_observation_and_backend_changes(self):
        a = result(); b = copy.deepcopy(a); b['run_dir'] = 'other'; b['steps'][0]['elapsed_seconds'] = 900
        self.assertFalse(compare_results(a, b)['different'])
        b['steps'][0]['observed']['text']['sha256'] = 'changed'
        self.assertTrue(compare_results(a, b)['different'])
        b['backend'] = 'windows-uia'
        self.assertFalse(compare_results(a, b)['comparable_backend'])

    def test_repeat_does_not_infer_a_population_flake_rate(self):
        s = summarize_repeats([result(), result('FAIL'), result()])
        self.assertEqual((s['runs'], s['passed'], s['failed'], s['mixed_outcomes']), (3, 2, 1, True))
        self.assertIn('sample only', s['interpretation'])

    def test_minimizer_preserves_failure_signature_and_budget(self):
        script = {'version': 1, 'name': 'x', 'steps': [{'id': n} for n in range(5)]}
        attempts = []
        def evaluate(s):
            attempts.append(s)
            ids = [x['id'] for x in s['steps']]
            if 1 in ids and 4 in ids: return result('FAIL')
            # A different failure is not a valid reduction.
            return result('FAIL', step_hash='missing-precondition')
        reduced = minimize(script, evaluate, max_attempts=10)
        self.assertEqual([s['id'] for s in reduced['script']['steps']], [1, 4])
        self.assertLessEqual(len(attempts), 10)
        self.assertTrue(reduced['one_minimal'])

    def test_minimizer_rejects_passing_baseline(self):
        with self.assertRaises(ValueError):
            minimize({'steps': []}, lambda s: result(), max_attempts=2)
