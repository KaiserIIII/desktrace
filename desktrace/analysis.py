"""Bounded engineering helpers; no statistical/generalization claims."""
import copy
import json


def normalized(result):
    fields = ('action', 'status', 'code', 'step_sha256', 'observed', 'locator_quality')
    return {'status': result['status'], 'backend': result['backend'],
            'script_sha256': result.get('script_sha256'),
            'steps': [{k: s[k] for k in fields if k in s} for s in result['steps']]}


def compare_results(left, right):
    a, b = normalized(left), normalized(right)
    return {'different': a != b, 'comparable_backend': left['backend'] == right['backend'],
            'same_script': left.get('script_sha256') == right.get('script_sha256') if left.get('script_sha256') and right.get('script_sha256') else 'UNKNOWN',
            'left': a, 'right': b,
            'interpretation': 'Outcome/text-hash comparison only; runtime, process identity and image pixels are excluded.'}


def summarize_repeats(results):
    if not results: raise ValueError('At least one result is required')
    passed = sum(r['status'] == 'PASS' for r in results)
    return {'runs': len(results), 'passed': passed, 'failed': len(results) - passed,
            'mixed_outcomes': 0 < passed < len(results),
            'outcome_variants': len({json.dumps(normalized(r), sort_keys=True) for r in results}),
            'same_backend': len({r['backend'] for r in results}) == 1,
            'same_script': len({r.get('script_sha256') for r in results}) == 1 if all(r.get('script_sha256') for r in results) else 'UNKNOWN',
            'interpretation': 'Descriptive sample only. Reset/isolation are caller responsibilities; no deployment flake-rate estimate.'}


def failure_signature(result):
    if result['status'] != 'FAIL' or result['failure_step'] is None:
        return None
    failure = result['steps'][result['failure_step']]
    # Never accept a generic provider/locator error as a reproduced assertion failure.
    if failure['code'] not in ('ASSERT_TEXT', 'ASSERT_STATE'):
        return None
    return {k: failure.get(k) for k in ('action', 'code', 'step_sha256', 'observed')}


def minimize(script, evaluate, *, max_attempts=12):
    """Greedy deletion using a fresh owned app per evaluate call. No action replay retry.

    The caller must provide deterministic reset and retain every result. A matched
    signature is a local engineering heuristic, not semantic-equivalence proof.
    """
    if type(max_attempts) is not int or not 1 <= max_attempts <= 50:
        raise ValueError('Budget must be 1..50')
    current = copy.deepcopy(script)
    baseline = evaluate(copy.deepcopy(current))
    goal = failure_signature(baseline)
    if goal is None: raise ValueError('A reproducible assertion failure is required')
    attempts = 1
    changes = []
    while attempts < max_attempts:
        changed = False
        completed_pass = True
        for i in range(len(current['steps'])):
            if attempts >= max_attempts:
                completed_pass = False
                break
            trial = copy.deepcopy(current)
            del trial['steps'][i]
            outcome = evaluate(copy.deepcopy(trial))
            attempts += 1
            if failure_signature(outcome) == goal:
                changes.append({'attempt': attempts, 'removed_current_index': i, 'remaining_steps': len(trial['steps'])})
                current = trial
                changed = True
                break  # Restart: previous removals can change which steps are necessary.
        if not changed and completed_pass:
            return {'script': current, 'attempts': attempts, 'one_minimal': True, 'changes': changes, 'failure_signature': goal}
        if not changed:
            break
    return {'script': current, 'attempts': attempts, 'one_minimal': not current['steps'], 'changes': changes, 'failure_signature': goal}
