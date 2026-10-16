# Validation record

This document distinguishes actual desktop execution, simulated adapter tests and unexecuted scope. The work is an engineering prototype; no research contribution or deployment reliability is claimed.

## Observed environment

Windows 11 build 26200, 64-bit CPython 3.13.0. Native dependencies: pywinauto 0.6.9, comtypes 1.4.17, pywin32 312, six 1.17.0. Build tooling setuptools 84.0.0; initial venv pip 24.2. Fresh virtual environments are project-local. Desktop probe showed session 1, active console 1, WinSta0/Default. Our tests use fresh non-visible desktops and only owned public fixtures.

## Completed initial checks

| Check | Outcome | Local evidence |
| --- | --- | --- |
| Full unit/integration suite | PASS, 41 tests | `runs/verification-6399762b083c41b7982ceca88fe9c589/00.stderr.log` |
| Dependency consistency; mock CLI PASS/FAIL/invalid/authorization; manifest | PASS | Same directory, `commands.json` and full logs |
| Real WinForms UIA six-step record/restart/replay | PASS | `runs/native-demo-ab9b317f1c094347a46ba65d41646535/summary.json` |
| Real intentional failure, PNG, HTML/JSON and manifest | PASS; PNG manually inspected upright at 636×339 | Same native directory; failure run `20261016T144602Z-e9db0f4fadc94444a97b45692db4e2af` |
| Real password-control block and duplicate-locator refusal | PASS | Same directory, separate password/duplicate run bundles |
| Real CLI enumerate/inspect/record/Unicode/restart/replay/fail/verify | PASS; replay exits 0 and 2 as intended | `runs/native-cli-9086dee5f56f40c8a16701810ab7f41d/commands.json` |
| Real Tk GUI render and recording/replay callbacks | PASS; screenshot inspected | `runs/gui-smoke-f10a88d443c54c62a4c524e05882563e/summary.json` |
| Three fresh-process repeated native runs and outcome diff | PASS, 3/3; one normalized outcome variant | `runs/extended-native-62debbfc212d4eb594fb55aeada3157e/repeat.json` |
| Bounded native failure minimization | PASS, 7→3 steps, 15 evaluations, tested one-step minimality | Same directory, `plan.json`, `minimized.json`, `progress.json`; every evaluation retained |

The GUI smoke programmatically invokes UI callbacks while Tk renders and pumps messages. It does not test physical mouse/keyboard navigation, native file-picker interactions or human usability. Native demo cleanup terminates only the owned held process handles; no graceful close/save-dialog behavior is claimed.

## Failed attempts retained

- `runs/native-demo-b68163168d614156b5812296aca019e8`: multiple same-PID input-method helper windows made the fixture launch ambiguous. The harness now uses an explicit fixture window-class constraint.
- `runs/native-demo-d08044d701324ee4b676914709e6ab0e`: hidden-desktop UIA offscreen status prevented semantic input. The corrected path permits only private-desktop controls with visible native HWNDs and never injects physical input.
- `runs/native-demo-20fb26dd261c400a9a8a85f94795091e`: unsupported pywin32 `IsZoomed` API. Reproduced with actual traceback; replaced by supported window-placement inspection and regression test.
- `runs/native-demo-71e79fe224fe431bbf9c84983e744eb1`: execution checks passed but its initial capture was oversized/upside down. The saved `PASS` described successful image creation only and is **not accepted visual-capture evidence**. DPI and explicit top-down DIB corrections were visually revalidated in the later run above. Original files were not rewritten.
- `runs/gui-smoke-a4997847f56546c4a5b5f6af987f41d6`: Tcl resource lookup failed in this Windows venv. Same-base-install resource discovery was added, without OS changes.
- `runs/gui-smoke-b89cbbeb5f2c41e981c4c45665cc94d0`: GUI callbacks passed, but screenshot querying its provider blocked the same Tk message loop and timed out. The harness was corrected to pump Tk during the capture worker. No timeout was converted to a pass.
- Dependency download via the configured pip index was slow and interrupted. Official PyPI artifact URLs were then used with exact hashes. The initial assumed comtypes `v1.4.17` tag did not exist; actual tag `1.4.17` and commit were resolved through GitHub before installation.

## NOT RUN and limits

System Notepad E2E: **NOT RUN**. A bounded private-desktop launch probe found no unique owned `Notepad` class window for the launched PID. No user Notepad session or other desktop window was attached. `runs/notepad-probe-*/probe.json` records this limitation; `tools/notepad_probe.py` provides a repeatable availability probe. Do not describe the WinForms fixture as Notepad or a system app.

Also NOT RUN: physical-input GUI acceptance, Windows versions/architectures other than the stated host, Linux/native desktop support, RDP/locked/service/elevated sessions, broad third-party application compatibility, GPU/custom controls, real intermittent-failure detection and deployment false-positive/false-negative rates, comprehensive dependency-CVE/binary security scanning. Mock tests verify engine behavior, not native Windows support in another environment.

## Final clean-checkout gate

Initial source verification is complete. A new local Git checkout, fresh venv install from the reviewed lock, installed-package use from an unrelated working directory, and full/native validation are the next gate. They are not marked PASS until the new checkout has actually executed. Final results will be appended here with their command/evidence paths.
