# Independent Windows VM acceptance — 2026-10-17

Status: **PASS WITH SCOPE LIMITATIONS**. All eight planned engineering gates were actually executed and passed. This is not a public release authorization.

## Scope and provenance

The tested source archive contains the 53 tracked files from commit
`4ede97c5293c3d59378977d846ca76b9fd9bda81`. The `desktrace/` Git tree is
`b233515b42ba2082b6f4a86792a861534aa825a8`. Current installation-documentation
corrections do not change that implementation, its tests, wheel lock or tools.

A new Windows Server 2022 Standard Evaluation **Desktop Experience** guest
(build 20348), CPython 3.13.0 x64, QEMU/WHPX, four virtual CPUs and 6 GiB RAM
was provisioned from Microsoft's official evaluation media on a new sparse
virtual disk. No guest network adapter, host physical disk or writable host
data share was attached. Input media was read-only. Tests installed the frozen
package normally into fresh guest virtual environments, using five reviewed,
hash-locked offline wheels. Guest paths do not depend on the original host
checkout. This is an independent Windows Server desktop validation; it is not
an independent Windows 11 client validation.

## Confirmed results

| Check | Actual result |
| --- | --- |
| Offline dependency/package install and installed CLI startup | PASS |
| Full unit/CLI/boundary suite | PASS, 41 tests |
| Native fixture recording/Unicode/Invoke/restart/replay/failure evidence | PASS |
| Native CLI and bundle verification | PASS |
| Character Map system-app flow | PASS |
| Tk rendering and callback smoke | PASS; callbacks, not native-input navigation |
| Fresh-process repeat and bounded failure minimization | PASS; 3/3, 7 to 3 steps in 15 evaluations, one-step minimality |
| Uninstall, import absent from neutral working directory, evidence retained, reinstall | PASS |
| Real classic system Notepad Unicode input/readback, close/relaunch/JSON replay | PASS |
| Intentional Notepad failure, target PNG, HTML/JSON and manifest | PASS; PNG visually inspected |
| Native GUI/input/file-picker/window-switch/resolution acceptance | PASS in the second freshly provisioned guest; details below |

The successful automated kit ran 15 recorded commands and retained its original
`AUTOMATED_GATE_PASS_MANUAL_PENDING` status. A separate real Notepad test
completed afterwards. Its screenshot visibly contains the supplied Chinese,
Greek, accented Latin and Japanese test text. Sixty-two transferred run
manifests were reverified successfully for the first guest's transfer. The second
guest also passed all 15 kit commands and a separate Notepad run. Its transferred
evidence and final GUI evidence passed 68 manifest checks; overlapping retained
copies are included. Neither count represents independent test cases.

The final GUI driver used actual native mouse/keyboard input against the real
Tk recorder, not direct calls to `App` callbacks. It passed:

- Explicit target selection and authorization, Unicode operation recording.
- Native Save/Open file dialogs, a Chinese JSON filename, load and replay.
- Foreground switching to a distinct owned decoy; its input stayed unchanged.
- Complete recorder process exit/restart, fresh binding, loading saved JSON and replay.
- Guest resolution change from 1024×768 to 1280×1024 and successful replay;
  the original resolution was restored. Changed DPI remains NOT RUN.

The recorder still records explicit UIA operations; testing its own GUI with
native input does not add a passive mouse/keyboard recording feature. Human
usability remains NOT RUN.

## Failures retained and prerequisite correction

The first fresh installation passed unit/CLI tests but native operations failed:
pywinauto imported pywin32's `win32ui`, whose `mfc140u.dll` system dependency was
absent. The DLL import was independently identified in the PE import table.
Before installing Microsoft's signed Visual C++ x64 runtime, the import exited
1; afterwards it exited 0. The installer exited 0. The same frozen native tools
then passed in a second fresh venv. The runtime artifact and its distribution
boundary are recorded in [SYSTEM_PREREQUISITES.json](../SYSTEM_PREREQUISITES.json).
No project algorithm or Python dependency was upgraded.

The first native-input GUI acceptance was interrupted by a test observer's
Windows file-sharing violation while replacing its state JSON. That failure is
retained. The observer now schedules the next observation after a transient
sharing violation; product callbacks and success criteria were not changed.
The guest subsequently reached its configured automatic-login limit. Its lock
screen was not automated. The first VM was shut down normally and retained;
a second fresh guest was provisioned for the corrected GUI acceptance. Its
native recording and save succeeded, while the first file-dialog driver used a
venv launcher PID instead of the observed Tk process PID. A later driver also
assumed Explorer's Open control was a plain UIA Button, rather than a split
button. These test-driver failures, their inputs, actual window inventory and
screenshots are retained. The final driver bound the actual observed process,
held its handle for cleanup, and verified the native dialog's IDOK caption,
process and state before clicking. The same success criteria then passed.

QEMU's WHPX warm reset failed once with `Unexpected VP exit code 4`; controlled
cold starts with `-no-reboot` resumed installation. The SDL backend hung once;
only the verified owned VM process was terminated. QEMU Guest Agent process
launch failed because its helper program was absent; guest-only startup scripts
ran the tests instead, and official guest-file RPCs transferred evidence. These
are infrastructure observations, not DeskTrace defects or scientific findings.

## Evidence and remaining scope

Original inputs, scripts, stdout/stderr, command argv/CWD/exit codes, screenshots,
reports, package manifests, before/after import logs and failed attempts are
retained in the owner's independent VM lab directory. Raw VM media, guest-only
credentials, installer binaries and original logs are deliberately outside this
repository. [The bounded summary](../evidence/VALIDATION_SUMMARY.json) includes
environment, gates and hashes of retained archives, without guest credentials,
installers or original logs. It does not replace the raw records. Both owned
guests were shut down normally; test-only startup was disabled, the second VM
received an `acceptance_completed` snapshot, and no host startup task/service
was installed.

Still unqualified: independent Windows 11 client installation, changed DPI,
RDP/locked/service/cross-privilege operation, human usability, broad application
compatibility, real deployment flakiness and comprehensive security/CVE auditing.
Existing scientific **NO-GO** conclusions are unchanged.
