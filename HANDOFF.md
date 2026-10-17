# Developer handoff

Work only in this DeskTrace directory or a fresh checkout. Do not modify PatchVerdict, Research Discovery or CardCraft. No DeskTrace public remote/push/release/deployment is authorized. The owner permits local Git commits.

## Start

Follow the exact Windows 3.13 x64 commands in [README.md](README.md), including the native import check. A clean Windows VM also needed Microsoft's Visual C++ x64 MFC runtime; [SYSTEM_PREREQUISITES.json](SYSTEM_PREREQUISITES.json) records the tested official artifact. Its system installer may require administrator rights; DeskTrace itself does not. Do not run an unreviewed dependency upgrade: [requirements-windows.lock](requirements-windows.lock) and [DEPENDENCIES.json](DEPENDENCIES.json) pin reviewed versions, source references and wheel hashes. `tools/fetch_wheels.py` downloads official artifacts only. Use a new venv, then install the project with `--no-build-isolation --no-deps` after the lock. No security-setting changes are needed.

Use `python -m desktrace gui` for interactive explicit recording, or `windows` → `inspect --hwnd … --pid … --authorize` → `record`/`replay` on a disposable test app. The recorder executes explicit UIA Value/Invoke operations; it does not record arbitrary physical mouse clicks, drag paths or key streams. Never test a private browser, messenger, password manager, terminal or security dialog.

## Reproduce evidence

Run in order with the new venv interpreter:

```powershell
python tools/verify.py
python tools/native_demo.py
python tools/native_cli_demo.py
python tools/system_app_demo.py
python tools/gui_smoke.py
python tools/extended_native_demo.py
```

These commands create new directories under ignored `runs/` and do not erase old attempts. The first native command compiles only `tools/Fixture.cs` with the existing Windows .NET Framework compiler; later demos use that own fixture. Lack of the compiler/private desktop/UIA provider must be reported as an environment blocker, not replaced with mock output. A system-app availability probe is available as `tools/notepad_probe.py`; it does not itself execute or certify a system-app E2E.

Open `report.html` from the actual run directory. `python -m desktrace verify RUN` checks file hashes; `compare LEFT RIGHT` compares normalized outcome/text hashes; `summarize RUN1 RUN2 RUN3` describes an existing sample. Inspect original input/expected strings locally through `script.json`, since result observations are hashed. Review images privately before sharing.

## Module map

`model`/`privacy`: contracts and guards. `engine`: recorder/assertions/runs. `adapters/windows` + `uia_worker`: bounded real UIA and target-only capture. `adapters/mock`: explicitly labeled simulation. `report`/`image`: artifacts and PNG. `analysis`: comparison/repetition summary/minimization. `gui`/`cli`: user clients. `tools`: owned fixture/lifecycle, verification and demo harnesses. `tests`: unittest behavior/CLI/boundary regression tests.

## Recovery

Read [RESUME.md](RESUME.md), [VALIDATION.md](VALIDATION.md), [docs/REVIEW.md](docs/REVIEW.md) and [SECURITY.md](SECURITY.md) before resuming. Preserve failed runs, source snapshots and original logs. Native tests never switch the user's visible desktop. A timeout means unknown target outcome: stop, inspect/reset the owned app and establish a fresh binding. Do not blindly retry inputs.

Recording writes the final script at save/EOF; if interrupted earlier, retain/reconstruct from the single-operation evidence bundles. A partial run without the required files/final manifest is incomplete. Do not manually manufacture a missing result or change successful/failed status. New defects need a reproduction and behavioral regression test before a narrow fix.

## Next useful task

Independent Windows Server desktop acceptance is complete; see [the actual gates and retained failures](docs/VM_ACCEPTANCE.md). A source-only experimental alpha is technically qualified within that stated scope. Keep private-desktop fixtures, native recorder input and real Notepad as separate evidence tiers. The next useful validation is an independent Windows 11 client guest before expanding the supported-environment claim. Installer packaging and a demo video are not delivered. A public repository, push or release still requires separate explicit authorization. Existing results do not support general compatibility, real-world flake rates or scientific novelty.
