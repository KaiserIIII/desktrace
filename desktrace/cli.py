"""CLI: JSON on stdout, bounded error codes on stderr; 0/2/1 pass/fail/error."""
import argparse
import json
from pathlib import Path
import sys
from .adapters.mock import MockAdapter
from .adapters.windows import WindowsAdapter, list_windows
from .engine import Recording, replay
from .model import DeskTraceError, load_script, require
from .report import verify_bundle
from .analysis import compare_results, summarize_repeats


def adapter_for(args):
    if getattr(args, 'backend', 'windows') == 'mock':
        return MockAdapter()
    require(args.authorize, 'AUTHORIZATION_REQUIRED')
    require(args.hwnd is not None and args.pid is not None, 'TARGET_REQUIRED')
    return WindowsAdapter(args.hwnd, args.pid, timeout=args.timeout,
                          desktop=args.desktop, allow_screenshot=args.allow_screenshot)


def parser():
    p = argparse.ArgumentParser(prog='desktrace', description='Local desktop regression lab. Use only authorized non-sensitive test windows.')
    sub = p.add_subparsers(dest='command', required=True)
    w = sub.add_parser('windows', help='List HWND/PID/classes; titles are opt-in')
    w.add_argument('--include-titles', action='store_true')
    w.add_argument('--desktop')
    sub.add_parser('gui', help='Open the explicit-operation recorder GUI')
    verify = sub.add_parser('verify', help='Check a run manifest; does not authenticate origin')
    verify.add_argument('run')
    compare = sub.add_parser('compare', help='Compare verified run outcomes and text hashes')
    compare.add_argument('left'); compare.add_argument('right')
    repeats = sub.add_parser('summarize', help='Describe an existing repeated-run sample')
    repeats.add_argument('runs', nargs='+')
    for name in ('inspect', 'record', 'replay'):
        c = sub.add_parser(name)
        c.add_argument('--backend', choices=('windows', 'mock'), default='windows')
        c.add_argument('--hwnd', type=lambda v: int(v, 0))
        c.add_argument('--pid', type=int)
        c.add_argument('--authorize', action='store_true', help='Confirm this selected window and test data are authorized and non-sensitive')
        c.add_argument('--allow-screenshot', action='store_true', help='Opt in to selected-window failure screenshots')
        c.add_argument('--desktop', help='Existing DeskTrace- private desktop, for controlled test harnesses')
        c.add_argument('--timeout', type=float, default=15)
        if name == 'record':
            c.add_argument('--out', required=True)
            c.add_argument('--name', default='Recorded test')
            c.add_argument('--runs', default='runs')
        if name == 'replay':
            c.add_argument('script')
            c.add_argument('--runs', default='runs')
    return p


def emit(value, stream=None):
    print(json.dumps(value, ensure_ascii=False, indent=2), file=stream or sys.stdout)


def main(argv=None):
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf8')
    args = parser().parse_args(argv)
    try:
        if args.command == 'gui':
            from .gui import main as gui_main
            gui_main()
            return 0
        if args.command == 'windows':
            emit(list_windows(desktop=args.desktop, include_titles=args.include_titles))
            return 0
        if args.command == 'verify':
            good = verify_bundle(Path(args.run))
            emit({'status': 'PASS' if good else 'FAIL'})
            return 0 if good else 2
        if args.command in ('compare', 'summarize'):
            paths = [args.left, args.right] if args.command == 'compare' else args.runs
            require(len(paths) <= 50, 'RESULT_LIMIT')
            results = []
            for path in paths:
                require(verify_bundle(Path(path)), 'INVALID_EVIDENCE_BUNDLE')
                results.append(json.loads((Path(path) / 'result.json').read_text(encoding='utf8')))
            emit(compare_results(*results) if args.command == 'compare' else summarize_repeats(results))
            return 0
        # Validate all replay input before binding to any native application.
        script = load_script(args.script) if args.command == 'replay' else None
        adapter = adapter_for(args)
        if args.command == 'inspect':
            require(hasattr(adapter, 'inspect'), 'INSPECT_REQUIRES_WINDOWS')
            emit(adapter.inspect())
            return 0
        if args.command == 'record':
            require(not Path(args.out).exists(), 'OUTPUT_EXISTS')
            recording = Recording(adapter, args.name, runs=args.runs)
            # JSON lines are explicit authorized commands; no system event listener exists.
            for line in sys.stdin:
                require(len(line) <= 20000, 'STEP_TOO_LARGE')
                if line.strip():
                    recording.add(json.loads(line))
            recording.save(args.out)
            emit({'status': 'PASS', 'steps': len(recording.script['steps']), 'script': str(args.out)})
            return 0
        result = replay(script, adapter, args.runs)
        emit(result)
        return 0 if result['status'] == 'PASS' else 2
    except DeskTraceError as error:
        emit({'error': error.code, **({'evidence': error.evidence} if error.evidence else {})}, sys.stderr)
    except (ValueError, UnicodeError):
        emit({'error': 'INVALID_INPUT'}, sys.stderr)
    except OSError:
        emit({'error': 'IO_ERROR'}, sys.stderr)
    except Exception:
        emit({'error': 'UNEXPECTED_ERROR'}, sys.stderr)
    return 1
