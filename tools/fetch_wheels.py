"""Download only the reviewed official artifacts and verify every SHA-256."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / 'vendor/wheels'
    target.mkdir(parents=True, exist_ok=True)
    specs = json.loads((ROOT / 'DEPENDENCIES.json').read_text(encoding='utf8'))
    def fetch(spec):
        url = spec['download_url']
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname != 'files.pythonhosted.org' or not spec.get('reviewed_commit'):
            raise ValueError('Unreviewed artifact source')
        path = target / spec['wheel']
        if path.name != spec['wheel']:
            raise ValueError('Invalid wheel name')
        if path.exists():
            data = path.read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=60) as response:
                if urllib.parse.urlsplit(response.url).hostname != 'files.pythonhosted.org':
                    raise ValueError('Unexpected redirect')
                data = response.read(30_000_001)
        if len(data) > 30_000_000 or hashlib.sha256(data).hexdigest() != spec['sha256']:
            raise ValueError('Artifact hash mismatch')
        if not path.exists():
            with path.open('xb') as f: f.write(data)
        return spec['wheel']
    with ThreadPoolExecutor(max_workers=5) as pool:
        for name in pool.map(fetch, specs):
            print('VERIFIED', name)


if __name__ == '__main__':
    main()
