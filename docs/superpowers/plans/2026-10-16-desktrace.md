# DeskTrace implementation plan

**Goal:** Deliver a local Windows regression recorder/replayer with bounded target access and truthful evidence.

**Architecture:** A validated JSON script drives an adapter through a replay engine. The native adapter delegates UIA to pywinauto in disposable worker processes. A mock adapter tests engine behavior without claiming desktop execution. A Tk GUI uses the same recording and replay interfaces as the CLI.

**Tech stack:** Python 3.13, unittest, Tkinter, pinned pywinauto UIA and its dependencies. No network service or global hooks.

The user requests autonomous implementation, so design choices and review checkpoints are recorded here without waiting for replies. This is a new isolated directory; no existing project is edited.

## Constraints

- One explicitly selected HWND + PID + process creation identity per session; fail closed on window replacement.
- Explicit command recording only. No global keyboard/mouse hooks, coordinate fallback, terminal automation, arbitrary script execution or authentication automation.
- Block password controls before reading text. Only authorized non-sensitive test data. Screenshots require separate opt-in and are skipped if password controls are present.
- Evidence is local, runs use new UUID directories, logs contain text hashes/lengths rather than actual text. JSON scripts necessarily contain supplied test data.
- Real UIA, fixture, system-app and mock results must have distinct labels. Unsupported native execution is NOT RUN.
- No remote repository, push, release or research novelty claim.

## Steps and verification gates

1. [ ] Save fixed upstream SHAs, license/release metadata and source documentation; create hashed dependency lock and isolated environment. Inspect pywinauto's selector, Invoke, Value/Text and window APIs before implementation.
2. [ ] Write failing behavioral tests for script validation, privacy, unique selection, recorder persistence, assertions, run evidence, HTML escaping and timeout handling. Execute them before creating the corresponding modules.
3. [ ] Implement `model.py`, `privacy.py`, `engine.py`, `report.py`, `adapters/mock.py`. Interface: `adapter.perform(step) -> dict`; errors are typed `DeskTraceError(code)`. Recorder only appends after successful execution.
4. [ ] Add `adapters/windows.py` and `uia_worker.py`: subprocess timeout; bind HWND/PID/process-start; exact AutomationId/control-type selector, reject ambiguity, only UIA Invoke/Value actions; target-only PrintWindow capture.
5. [ ] Add CLI (`windows`, `inspect`, `record`, `replay`, `gui`) and Tk GUI. Save JSON using exclusive creation to avoid overwriting scripts. Tests verify CLI exit codes and Unicode.
6. [ ] Probe safe desktop capabilities. Launch a fresh non-sensitive owned app on a private desktop, exercise record/restart/replay/assertion failure/capture. Attempt system Notepad only if it exposes a fresh isolated window. Preserve all attempts.
7. [ ] After native MVP passes, prioritize repeat and JSON-result diff. Defer automatic minimization if reset/precondition safety cannot be guaranteed.
8. [ ] Run all tests in a clean environment, inspect evidence/report, review safety and scope, write README/architecture/research/security/validation/AI-extension/RESUME. Initialize local Git with verified owner identity, inspect tracked file boundaries and commit. No remote.

## Acceptance commands

`python -m unittest discover -s tests -v`

`python -m desktrace replay examples/mock.json --backend mock --runs runs`

`python tools/native_demo.py` (native outcome must be observed, never substituted by mock).

Every gate preserves command, exit code, environment and logs under `evidence/` or ignored `runs/`; final validation reports actual counts and missing coverage.
