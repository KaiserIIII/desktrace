"""Bounded repeat/diff/minimize experiment after the real native MVP gate."""
import copy
import json
from pathlib import Path
import sys
import uuid
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktrace.adapters.windows import WindowsAdapter
from desktrace.analysis import compare_results, summarize_repeats, minimize
from desktrace.engine import replay
from desktrace.report import write_json, verify_bundle
from private_desktop import PrivateDesktop


def main():
    summaries = list((ROOT / 'runs').glob('native-demo-*/summary.json'))
    accepted = [p for p in summaries if json.loads(p.read_text(encoding='utf8')).get('status') == 'PASS']
    if not accepted: raise RuntimeError('REAL_NATIVE_MVP_GATE_NOT_MET')
    previous = max(accepted, key=lambda p: p.stat().st_mtime).parent
    script = json.loads((previous / 'recorded.json').read_text(encoding='utf8'))
    out = ROOT / 'runs' / ('extended-native-' + uuid.uuid4().hex); out.mkdir(parents=True)
    # Written before collecting any data. No post-hoc success threshold changes.
    plan = {'kind': 'real-windows-uia', 'reset': 'Fresh owned fixture process for every evaluation',
            'repeat_count': 3, 'minimization_budget': 16,
            'success': {'repeat': 'All three pass; report sample only', 'diff': 'Same-script clean runs equal; intentional failure differs',
                        'minimize': 'Fewer steps retain exact assertion action/code/step hash/observed hash signature'},
            'nonclaims': ['No real deployment flake rate', 'No guarantee of global minimum', 'No semantic-equivalence proof']}
    write_json(out / 'plan.json', plan)
    all_results = []
    with PrivateDesktop() as desktop:
        def evaluate(s):
            pid = desktop.launch(previous / 'DeskTraceFixture.exe')
            try:
                w = desktop.wait_window(pid)
                a = WindowsAdapter(w['hwnd'], pid, desktop=desktop.name)
                r = replay(s, a, out)
                all_results.append(r)
                write_json(out / 'progress.json', {'completed_evaluations': len(all_results), 'runs': [x['run_dir'] for x in all_results]})
                return r
            finally:
                desktop.close_app(pid)
        repeated = [evaluate(script) for _ in range(plan['repeat_count'])]
        bad = copy.deepcopy(script)
        bad['steps'].append({'action': 'assert_text', 'locator': {'automation_id': 'output', 'control_type': 'Edit'}, 'expected': 'Intentionally different'})
        reduced = minimize(bad, evaluate, max_attempts=plan['minimization_budget'])
        write_json(out / 'minimized.json', reduced)
        comparison = compare_results(repeated[0], repeated[1])
        failure_diff = compare_results(repeated[0], all_results[3])
        write_json(out / 'repeat.json', summarize_repeats(repeated))
        write_json(out / 'compare_equal.json', comparison)
        write_json(out / 'compare_failure.json', failure_diff)
        summary = {'kind': 'real-windows-uia', 'directory': str(out), 'repeat': summarize_repeats(repeated),
                   'original_failing_steps': len(bad['steps']), 'minimized_steps': len(reduced['script']['steps']),
                   'minimizer_evaluations': reduced['attempts'], 'one_minimal': reduced['one_minimal'],
                   'checks': {'repeat': 'PASS' if all(r['status'] == 'PASS' for r in repeated) else 'FAIL',
                              'compare_equal': 'PASS' if not comparison['different'] else 'FAIL',
                              'compare_failure': 'PASS' if failure_diff['different'] else 'FAIL',
                              'minimize': 'PASS' if len(reduced['script']['steps']) < len(bad['steps']) else 'FAIL',
                              'all_manifests': 'PASS' if all(verify_bundle(Path(r['run_dir'])) for r in all_results) else 'FAIL'}}
        summary['status'] = 'PASS' if all(v == 'PASS' for v in summary['checks'].values()) else 'FAIL'
        write_json(out / 'summary.json', summary)
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
