"""Adapter-independent recorder and bounded, stop-on-failure replay."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import time
import uuid
from .model import DeskTraceError, validate_script, validate_step
from .privacy import fingerprint
from .report import finish_report, write_json


def execute(adapter, step):
    observed = adapter.perform(step)
    if step['action'] == 'assert_text' and observed.get('text') != step['expected']:
        raise AssertionFailure('ASSERT_TEXT', {'text': fingerprint(observed.get('text', ''))})
    if step['action'] in ('assert_control', 'assert_window') and observed.get(step['state']) != step['value']:
        raise AssertionFailure('ASSERT_STATE', {step['state']: observed.get(step['state'])})
    return {k: fingerprint(v) if k == 'text' else v for k, v in observed.items() if k in ('text', 'enabled', 'visible', 'exists', 'normal', 'minimized')}


class AssertionFailure(DeskTraceError):
    def __init__(self, code, observation):
        super().__init__(code)
        self.observation = observation


class Recording:
    def __init__(self, adapter, name, *, runs=None):
        self.adapter = adapter
        self.runs = runs
        self.script = validate_script({'version': 1, 'name': name, 'steps': []})

    def add(self, step):
        validate_script({**self.script, 'steps': self.script['steps'] + [step]})
        if self.runs is None:
            execute(self.adapter, step)
        else:
            # Execute once through the evidence pipeline, including failed recordings.
            result = replay({**self.script, 'steps': [step]}, self.adapter, self.runs)
            if result['status'] == 'FAIL':
                raise DeskTraceError(result['steps'][0]['code'], evidence=result['run_dir'])
        self.script['steps'].append(copy.deepcopy(step))

    def save(self, path):
        with Path(path).open('x', encoding='utf8') as f:
            json.dump(self.script, f, ensure_ascii=False, indent=2)
            f.write('\n')


def replay(script, adapter, runs):
    validate_script(script)  # Entire script is checked before any action or directory creation.
    run = Path(runs).resolve() / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex)
    run.mkdir(parents=True, exist_ok=False)
    write_json(run / 'script.json', script)
    result = {'format': 1, 'backend': adapter.kind, 'status': 'PASS', 'failure_step': None,
              'script_sha256': hashlib.sha256(json.dumps(script, sort_keys=True, ensure_ascii=False).encode('utf8')).hexdigest(),
              'started_at': datetime.now(timezone.utc).isoformat(), 'run_dir': str(run),
              'environment': {'python': platform.python_version(), 'system': platform.system(),
                              'release': platform.release(), 'adapter': adapter.environment()},
              'steps': [], 'screenshot': {'status': 'NOT RUN', 'reason': 'No failing step'}}
    with (run / 'events.jsonl').open('x', encoding='utf8') as events:
        for index, step in enumerate(script['steps']):
            start = time.monotonic()
            entry = {'index': index, 'action': step['action'], 'status': 'PASS', 'code': 'OK',
                     'locator_quality': 'automation_id' if step.get('locator', {}).get('automation_id') else 'name_only' if 'locator' in step else 'window',
                     'step_sha256': hashlib.sha256(json.dumps(step, sort_keys=True, ensure_ascii=False).encode('utf8')).hexdigest(),
                     'at': datetime.now(timezone.utc).isoformat()}
            try:
                entry['observed'] = execute(adapter, step)
            except DeskTraceError as error:
                entry.update(status='FAIL', code=error.code)
                if isinstance(error, AssertionFailure):
                    entry['observed'] = error.observation
            except Exception:
                entry.update(status='FAIL', code='ADAPTER_ERROR')  # Never persist raw provider exception text.
            entry['elapsed_seconds'] = round(time.monotonic() - start, 6)
            result['steps'].append(entry)
            events.write(json.dumps(entry, ensure_ascii=False) + '\n')
            events.flush()
            if entry['status'] == 'FAIL':
                result.update(status='FAIL', failure_step=index)
                try:
                    result['screenshot'] = adapter.capture(run / 'failure.png')
                except Exception:
                    result['screenshot'] = {'status': 'FAIL', 'reason': 'CAPTURE_ERROR'}
                break
    finish_report(run, result, script['name'])
    return result
