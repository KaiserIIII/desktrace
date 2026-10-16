"""Conservative guardrails, not a general personal-data detector."""
import hashlib
import re

SECRET = re.compile(r'(?:password|passwd|api[_-]?key|access[_-]?token|secret)\s*[:=]|-----BEGIN .*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9_]{20,}|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', re.I)


def sensitive(value):
    return bool(SECRET.search(value))


def fingerprint(text):
    return {'length': len(text), 'sha256': hashlib.sha256(text.encode('utf8')).hexdigest()}
