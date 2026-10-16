"""Deterministic simulated controls; never evidence of native desktop execution."""
from ..model import DeskTraceError


class MockAdapter:
    kind = 'mock'

    def __init__(self, duplicate=False, changed=False):
        self.controls = [dict(automation_id='input', control_type='Edit', name='Input', text='', password=False),
                         dict(automation_id='apply', control_type='Button', name='Apply', text='', password=False),
                         dict(automation_id='password', control_type='Edit', name='', text='', password=True)]
        if duplicate:
            self.controls.append(self.controls[0].copy())
        self.changed = changed
        self.calls = 0

    def environment(self):
        return {'simulated': True}

    def perform(self, step):
        self.calls += 1
        if self.changed:
            raise DeskTraceError('WINDOW_CHANGED')
        if step['action'] == 'assert_window':
            return {'exists': True, 'normal': True, 'minimized': False}
        controls = [c for c in self.controls if all(c.get(k) == v for k, v in step['locator'].items())]
        if not controls:
            raise DeskTraceError('LOCATOR_NOT_FOUND')
        if len(controls) != 1:
            raise DeskTraceError('AMBIGUOUS_LOCATOR')
        c = controls[0]
        if c['password']:
            raise DeskTraceError('PASSWORD_CONTROL_BLOCKED')
        if step['action'] == 'set_text':
            c['text'] = step['text']
        return {'text': c['text']} if step['action'] == 'assert_text' else {'enabled': True, 'visible': True}

    def capture(self, path):
        return {'status': 'NOT RUN', 'reason': 'Mock adapter does not capture images'}
