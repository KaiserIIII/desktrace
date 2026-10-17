# DeskTrace

**Local-first Windows Desktop Regression & Replay Lab.** Record explicit operations on one authorized test window, replay an editable JSON script, and keep a local failure bundle.

DeskTrace is an early engineering prototype built on [pywinauto UIA](https://github.com/pywinauto/pywinauto). It adds a small CLI/Tk workflow and evidence handling. It makes no research novelty, broad application-compatibility or production-reliability claim.

## What it does

- Enumerates HWND/PID/window classes. Window titles are opt-in.
- Binds a selected window to its PID, process creation time and window class. Replaced windows require a fresh binding.
- Explicitly executes and records UIA Value input and Invoke button activation. There is no passive mouse/keyboard recorder, global hook or coordinate fallback. Invoke is a semantic button action, not a physical mouse click.
- Replays text, enabled/visible-control, and exists/normal/minimized-window assertions.
- Stops on the first failure and saves JSON, JSONL, static HTML, input script and a SHA-256 manifest. Optional screenshots use only the target window's PrintWindow output.
- Compares outcome/text hashes, summarizes repeated runs, and offers a bounded minimization API for harnesses that reset their own test app.

The test script stores supplied test text in plain JSON. Observed text is represented by hashes/lengths in results and logs. Screenshots can contain visible personal information. Use disposable non-sensitive test applications; read [SECURITY.md](SECURITY.md).

## Install on Windows

Reviewed native environment: **64-bit CPython 3.13 on Windows**. Install Python with Tcl/Tk support. Use an interactive, unlocked test session with apps at the same privilege level; administrator access and Developer Mode are not required by DeskTrace. UIA cannot automate every custom-drawn control.

On a clean Windows installation, also install Microsoft's [Visual C++ v14 x64 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist). Its MFC runtime (`mfc140u.dll`) is needed by `pywin32`'s `win32ui`, which pywinauto imports. Python and the locked wheels alone did not supply it in our fresh VM. Installing this system prerequisite may require administrator rights; running DeskTrace does not. The exact independently tested artifact is recorded in [SYSTEM_PREREQUISITES.json](SYSTEM_PREREQUISITES.json). Download the runtime from Microsoft; it is not bundled with this project.

From the project root in PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe tools/fetch_wheels.py
.\.venv\Scripts\python.exe -m pip install --no-index --find-links vendor\wheels --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps .
.\.venv\Scripts\python.exe -c "import win32ui, pywinauto; print('Native dependencies OK')"
.\.venv\Scripts\python.exe -m desktrace --help
```

The downloader fetches only reviewed files from files.pythonhosted.org and checks their recorded hashes. [DEPENDENCIES.json](DEPENDENCIES.json) records repositories, source commits, versions, licenses and artifact hashes. Wheels are not redistributed in Git. The native wheel lock targets CPython 3.13 x64; other architectures/versions need a separately reviewed lock.

For a simulated tour that does not operate the desktop:

```powershell
.\.venv\Scripts\python.exe -m desktrace replay examples/mock.json --backend mock --runs runs
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Mock bundles identify themselves as `mock` and contain no fake screenshot.

## Record and replay a selected test window

Start a disposable test application yourself, then enumerate and inspect it:

```powershell
.\.venv\Scripts\python.exe -m desktrace windows
.\.venv\Scripts\python.exe -m desktrace inspect --hwnd 123456 --pid 1234 --authorize
.\.venv\Scripts\python.exe -m desktrace gui
```

Replace the example HWND/PID with actual values. In the GUI, check authorization, select a window, bind it, select a unique control, and use **Execute + record**. Edit the JSON as needed; **Replay editor** uses that JSON. Save creates a new file and never replaces an existing script. After restarting the target application, select and bind its new window before replaying the same script.

The CLI recorder reads one explicit JSON operation per stdin line. For our own fixture, create `operations.jsonl` with:

```jsonl
{"action":"set_text","locator":{"automation_id":"input","control_type":"Edit"},"text":"DeskTrace public test"}
{"action":"assert_text","locator":{"automation_id":"input","control_type":"Edit"},"expected":"DeskTrace public test"}
```

```powershell
Get-Content -Encoding UTF8 operations.jsonl | .\.venv\Scripts\python.exe -m desktrace record --hwnd 123456 --pid 1234 --authorize --out recorded.json
.\.venv\Scripts\python.exe -m desktrace replay recorded.json --hwnd 123456 --pid 1234 --authorize --allow-screenshot --runs runs
.\.venv\Scripts\python.exe -m desktrace verify runs\ACTUAL_RUN_DIRECTORY
```

Use the AutomationId/control type exposed by your own app. Ambiguous selectors fail; name-only selectors are permitted but labeled weaker and can depend on localization. A unique AutomationId today does not prove stability after restart or upgrade. No silent locator healing takes place. See the [input contract](docs/INPUT_CONTRACT.md).

Exit codes: `0` accepted command/passing replay, `2` failed replay/integrity verification, `1` invalid input, missing authorization or runtime error. A recording operation that fails exits `1` with an evidence path and is not added to the script. Argument-parser usage errors also exit `2`; read the JSON output/error and subcommand, not just the exit code.

## Actual demonstrations

```powershell
.\.venv\Scripts\python.exe tools/verify.py
.\.venv\Scripts\python.exe tools/native_demo.py
.\.venv\Scripts\python.exe tools/native_cli_demo.py
.\.venv\Scripts\python.exe tools/system_app_demo.py
.\.venv\Scripts\python.exe tools/gui_smoke.py
.\.venv\Scripts\python.exe tools/extended_native_demo.py
```

The native demos compile our MIT-licensed WinForms fixture with the existing Windows .NET Framework C# compiler. They launch only owned processes on a fresh non-visible `DeskTrace-…` desktop, never switch the user's visible desktop, and retain results under `runs/`. This is UI separation, **not a security sandbox**. Do not use it for untrusted applications. The GUI smoke invokes callbacks while rendering real Tk/UIA windows; it is not a physical-input usability test.

Real fixture UIA recording, Unicode input/readback, button invocation, restart/replay, intentional assertion failure and target screenshot have run successfully. The built-in **Windows Character Map** also completed input/readback, close/restart/replay and intentional failure with a real report. On the original Windows 11 host its TextPattern includes a final carriage return, explicitly represented in [the example](examples/charmap.json); no implicit text trimming occurs. That host's private-desktop Notepad probe found no unique owned window, so its Notepad E2E remains **NOT RUN**. Separately, a fresh **Windows Server 2022 Desktop Experience VM** passed real classic Notepad Unicode input/readback, close/relaunch/JSON replay and intentional failure with a real screenshot/report. These are different environments, not interchangeable results. See [independent VM acceptance](docs/VM_ACCEPTANCE.md) and [VALIDATION.md](VALIDATION.md) for actual gates, failures and remaining limits.

The independent Server VM also passed real native input on the recorder GUI, native file-dialog save/load with a Chinese filename, complete GUI restart/replay, target/decoy window switching and a resolution change from 1024×768 to 1280×1024. These are automated GUI acceptance results, not a human usability study or a claim of general Windows compatibility.

## Handoff

- [Architecture](docs/ARCHITECTURE.md), [input and evidence contracts](docs/INPUT_CONTRACT.md)
- [Upstream comparison](docs/UPSTREAM_RESEARCH.md), [third-party notices](THIRD_PARTY_NOTICES.md)
- [Security and limitations](SECURITY.md), [critical review](docs/REVIEW.md)
- [Future AI agent evaluation scope](docs/AGENT_EVALUATION_PLAN.md)
- [Resume/checkpoints](RESUME.md)

No remote repository, publication, release, telemetry or cloud service is configured. Public release requires a separate explicit decision. License: [MIT](LICENSE).
