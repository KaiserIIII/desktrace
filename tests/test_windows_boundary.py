import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from desktrace.model import DeskTraceError
from desktrace.adapters.windows import WindowsAdapter, worker_call
from desktrace.uia_worker import actionable, perform
from types import SimpleNamespace


class WorkerBoundaryTests(unittest.TestCase):
    def test_window_normal_uses_supported_placement_api(self):
        gui = SimpleNamespace(IsWindowVisible=lambda _: True, IsIconic=lambda _: False,
                              GetWindowPlacement=lambda _: (0, 1, (0, 0), (0, 0), (0, 0, 600, 300)))
        with patch('desktrace.uia_worker.root_for'), patch('desktrace.uia_worker.modules', return_value=(None, None, gui, None, None)):
            self.assertTrue(perform({'hwnd': 1}, dict(action='assert_window', state='normal', value=True))['normal'])

    def test_private_desktop_requires_native_visibility_for_offscreen_control(self):
        c = SimpleNamespace(is_enabled=lambda: True, is_visible=lambda: False,
                            element_info=SimpleNamespace(handle=123))
        gui = SimpleNamespace(IsWindowVisible=lambda hwnd: hwnd == 123)
        with patch('desktrace.uia_worker.modules', return_value=(None, None, gui, None, None)):
            self.assertFalse(actionable(c, False))
            self.assertTrue(actionable(c, True))
            c.is_enabled = lambda: False
            self.assertFalse(actionable(c, True))

    @patch('desktrace.adapters.windows.sys.platform', 'win32')
    def test_timeout_has_unknown_outcome_and_no_automatic_retry(self):
        with patch('desktrace.adapters.windows.subprocess.run', side_effect=subprocess.TimeoutExpired('uia', 1)) as run:
            with self.assertRaises(DeskTraceError) as cm:
                worker_call({'operation': 'perform'}, 1)
            self.assertEqual(cm.exception.code, 'WORKER_TIMEOUT_OUTCOME_UNKNOWN')
            self.assertEqual(run.call_count, 1)

    @patch('desktrace.adapters.windows.sys.platform', 'win32')
    def test_provider_error_does_not_expose_raw_stderr(self):
        p = subprocess.CompletedProcess([], 1, '', 'private provider text')
        with patch('desktrace.adapters.windows.subprocess.run', return_value=p):
            with self.assertRaises(DeskTraceError) as cm:
                worker_call({'operation': 'perform'})
            self.assertEqual(cm.exception.code, 'WORKER_FAILED')

    @patch('desktrace.adapters.windows.sys.platform', 'win32')
    def test_malformed_worker_response_rejected(self):
        for out in ('not json', '{}', '{"ok":true}'):
            p = subprocess.CompletedProcess([], 0, out, '')
            with self.subTest(out=out), patch('desktrace.adapters.windows.subprocess.run', return_value=p), self.assertRaises(DeskTraceError) as cm:
                worker_call({'operation': 'perform'})
            self.assertEqual(cm.exception.code, 'INVALID_WORKER_RESPONSE')

    def test_screenshot_requires_explicit_opt_in(self):
        with patch('desktrace.adapters.windows.worker_call', return_value={'hwnd': 100, 'pid': 200}) as rpc:
            a = WindowsAdapter(100, 200)
            self.assertEqual(a.capture('unused.png')['status'], 'NOT RUN')
            self.assertEqual(rpc.call_count, 1)

    def test_native_calls_include_frozen_binding(self):
        binding = {'hwnd': 100, 'pid': 200, 'created': 'identity'}
        with patch('desktrace.adapters.windows.worker_call', return_value=binding) as rpc:
            a = WindowsAdapter(100, 200)
            a.perform({'action': 'assert_window', 'state': 'exists', 'value': True})
            request = rpc.call_args.args[0]
            self.assertEqual(request['binding'], binding)
            self.assertEqual(request['operation'], 'perform')


if __name__ == '__main__':
    unittest.main()
