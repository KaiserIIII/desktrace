"""Static escaped HTML and integrity manifest. Hashes do not authenticate a run."""
import hashlib
import html
import json
from pathlib import Path


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finish_report(run, result, name):
    write_json(run / 'result.json', result)
    esc = html.escape
    rows = ''.join(f'<tr><td>{s["index"]}</td><td>{esc(s["action"])}</td><td>{s["status"]}</td><td>{esc(s["code"])}</td></tr>' for s in result['steps'])
    capture = result['screenshot']
    image = '<img alt="Selected test window on failure" src="failure.png">' if capture['status'] == 'PASS' else f'<p>Screenshot: {esc(capture["status"])} — {esc(capture.get("reason", ""))}</p>'
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'unsafe-inline'">
<title>DeskTrace {esc(result['status'])}</title><style>body{{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:1rem}}td,th{{padding:.5rem;border:1px solid #ccc}}table{{border-collapse:collapse}}img{{max-width:100%}}</style>
<h1>{esc(name)}</h1><p>{esc(result['status'])} · backend: {esc(result['backend'])} · {esc(result['started_at'])}</p>
<p>Text evidence uses hashes/lengths. This report is local and does not prove application correctness.</p>
<table><tr><th>Step (0-based)</th><th>Action</th><th>Status</th><th>Code</th></tr>{rows}</table>{image}
<p><a href="result.json">Machine result</a> · <a href="events.jsonl">Events</a> · <a href="script.json">Authorized test script</a></p></html>'''
    (run / 'report.html').write_text(page, encoding='utf8')
    files = {p.name: sha(p) for p in run.iterdir() if p.is_file() and p.name != 'manifest.json'}
    write_json(run / 'manifest.json', {'algorithm': 'sha256', 'files': files})


def verify_bundle(run):
    try:
        run = Path(run)
        manifest = json.loads((run / 'manifest.json').read_text(encoding='utf8'))
        files = manifest['files']
        if manifest['algorithm'] != 'sha256' or not isinstance(files, dict):
            return False
        if not {'result.json', 'script.json', 'events.jsonl', 'report.html'} <= set(files):
            return False
        if set(files) != {p.name for p in run.iterdir() if p.is_file() and p.name != 'manifest.json'}:
            return False
        return all(Path(n).name == n and not (run / n).is_symlink() and sha(run / n) == h for n, h in files.items())
    except (OSError, ValueError, KeyError, TypeError):
        return False
