"""Strict, versioned script contract. Scripts contain authorized public test data."""
import json
from pathlib import Path
from .privacy import sensitive


class DeskTraceError(Exception):
    def __init__(self, code, *, evidence=None):
        self.code = code
        self.evidence = evidence
        super().__init__(code)


def require(ok, code='INVALID_SCRIPT'):
    if not ok:
        raise DeskTraceError(code)


def text(value, limit=4096):
    require(isinstance(value, str) and len(value) <= limit)
    require(not sensitive(value), 'SENSITIVE_TEST_DATA')


def validate_step(step):
    require(isinstance(step, dict))
    action = step.get('action')
    fields = {'invoke': set(), 'set_text': {'text'}, 'assert_text': {'expected'},
              'assert_control': {'state', 'value'}, 'assert_window': {'state', 'value'}}
    require(isinstance(action, str) and action in fields)
    expected = {'action'} | fields[action] | (set() if action == 'assert_window' else {'locator'})
    require(set(step) == expected)
    if action != 'assert_window':
        loc = step['locator']
        require(isinstance(loc, dict) and set(loc) <= {'automation_id', 'control_type', 'name'})
        require(bool(loc.get('control_type')) and bool(loc.get('automation_id') or loc.get('name')))
        for value in loc.values():
            text(value, 256)
    for key in ('text', 'expected'):
        if key in step:
            text(step[key])
    if 'state' in step:
        states = {'enabled', 'visible'} if action == 'assert_control' else {'exists', 'normal', 'minimized'}
        require(isinstance(step['state'], str) and step['state'] in states and type(step['value']) is bool)
    return step


def validate_script(script):
    require(isinstance(script, dict) and set(script) == {'version', 'name', 'steps'})
    require(type(script['version']) is int and script['version'] == 1)
    text(script['name'], 200)
    require(isinstance(script['steps'], list) and len(script['steps']) <= 500)
    for step in script['steps']:
        validate_step(step)
    return script


def load_script(path):
    p = Path(path)
    require(p.stat().st_size <= 2_000_000, 'SCRIPT_TOO_LARGE')
    try:
        script = json.loads(p.read_text(encoding='utf-8-sig'))
    except (ValueError, UnicodeError):
        raise DeskTraceError('INVALID_JSON') from None
    return validate_script(script)
