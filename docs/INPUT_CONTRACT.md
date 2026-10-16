# Script and evidence contract v1

A script has exactly `version` (integer 1, not boolean), `name` (up to 200 characters), and `steps` (at most 500). Files are UTF-8 JSON, at most 2 MB when loaded by the CLI. Unknown fields/actions and unsupported types fail before any desktop action. Text is bounded to 4096 characters; locator strings to 256. Regex-like secret assignments, common token forms and email addresses are rejected as test data. This heuristic is not comprehensive PII detection.

Each non-window step requires `locator`: `control_type` plus `automation_id` or exact `name` (both may be supplied). No indexes, fuzzy matches, coordinates or executable code are accepted.

| Action | Required additional fields | Operation |
| --- | --- | --- |
| `set_text` | `locator`, `text` | UIA Value.SetValue; enabled and not read-only |
| `invoke` | `locator` | UIA Invoke.Invoke; semantic control activation |
| `assert_text` | `locator`, `expected` | Exact Value or Text-pattern text comparison |
| `assert_control` | `locator`, `state`, `value` | `state`: enabled/visible; `value`: boolean |
| `assert_window` | `state`, `value` | `state`: exists/normal/minimized; `value`: boolean |

`normal` means a visible, non-minimized/non-maximized Win32 window. A nonexistent window can satisfy `exists=false`; a handle reused by another identity is an error. Text comparison is exact, with no implicit normalization, substring matching or wait-until behavior. Each operation has one worker deadline (default 15 seconds, allowed 0.1–60), not an assertion retry loop. Reset/wait for application-specific readiness before running an assertion.

## Run directory

| File | Meaning |
| --- | --- |
| `script.json` | Exact accepted script including plain authorized test text |
| `events.jsonl` | Flushed completed-step events, zero-based index, UTC timestamp, elapsed seconds, result/code, locator quality, step hash |
| `result.json` | Format version, backend, overall status/failing index, script SHA-256, sanitized observations, minimal environment, screenshot disposition |
| `failure.png` | Optional actual selected-window capture; only present after successful capture |
| `report.html` | Escaped static local report, no remote resources or JavaScript |
| `manifest.json` | SHA-256 of every other regular file in the run |

Result text observations are `{length, sha256}`; they do not contain raw observed strings. Input test text and screenshots remain potentially private. Hashing is not encryption and low-entropy text can be guessed. The environment includes OS/Python/dependency versions and the bound HWND/PID/creation time/class, but no full environment dump, hostname or username collection. `run_dir` is an absolute local path and can itself disclose a username if shared.

`verify` checks required files, exact regular-file membership and hashes. It does not authenticate the manifest, execution, exit code or UI provider. `PASS` proves only that these scripted checks passed in this run. Neither missing coverage nor incomplete evidence is a pass.

Failure codes include `LOCATOR_NOT_FOUND`, `AMBIGUOUS_LOCATOR`, `WINDOW_GONE`, `WINDOW_CHANGED`, `PASSWORD_CONTROL_BLOCKED`, `PASSWORD_STATE_UNKNOWN`, `CONTROL_NOT_ACTIONABLE`, `CONTROL_READ_ONLY`, `PATTERN_UNAVAILABLE_OR_FAILED`, `TEXT_PATTERN_UNAVAILABLE`, `ASSERT_TEXT`, `ASSERT_STATE`, and `WORKER_TIMEOUT_OUTCOME_UNKNOWN`. Generic provider exceptions are redacted as `UIA_ERROR`/`ADAPTER_ERROR`. Use the step hash/index and original local script to locate the cause; do not enable raw provider logging on sensitive applications.

The adapter trusts the operating system, UIA provider's identity/password properties, user's authorization and public-data declaration. Screenshot scanning and identity checks have a race window and do not protect against a malicious application/provider. See [security](../SECURITY.md).
