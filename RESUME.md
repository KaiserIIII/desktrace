# DeskTrace resume checkpoint

## Current state

Engineering implementation and independent Windows VM acceptance are complete. The source-only experimental alpha is technically qualified within its stated scope. Keep this project local; no public remote, push, release or deployment is authorized. Existing scientific NO-GO conclusions remain unchanged. Read [PUBLICATION_DECISION.md](PUBLICATION_DECISION.md) before any scope change.

The implementation baseline is `c4c542fe1b1524eb1ebe688b0eef230d1561fe9c`. Later delivery documentation and the Character Map harness do not change `desktrace/` or its tests. Use `git rev-parse HEAD` for the final local SHA; this tracked document deliberately avoids a self-referential final SHA.

## Completed

- Fixed upstream/source/license research, hash-locked dependencies, isolated installation.
- Strict JSON, explicit recording, scoped UIA replay/assertions, deadlines, privacy guards, PNG/HTML/JSON evidence, CLI and Tk GUI.
- All 41 tests in fresh environments and a clean clone, installed package usage from an unrelated CWD.
- Real owned WinForms recording/Unicode/Invoke/close/restart/replay/intentional failure; real password and ambiguous-control probes.
- Real CLI and Tk callback/render tests; screenshots visually inspected.
- Three fresh-process repeated native runs; diff; 7→3 step failure reduction in 15 evaluations, all logs retained.
- Built-in Character Map Unicode/read/close/restart/replay/intentional failure/report. Its observed TextPattern final CR is explicit in the example; the first no-CR expectation failure is retained.
- Manual local source/privacy/release review and English handoff documents. This is not an independent professional security audit.
- Fresh Windows Server 2022 Desktop Experience guests: all 41 tests, 15 offline-kit commands, real native tools, installed CLI, uninstall/import absence and reinstall.
- Real classic Notepad Chinese/Unicode input/readback, close/relaunch/JSON replay, intentional failure and PNG/HTML/JSON/hash evidence.
- Native input on the real Tk recorder, native Save/Open dialogs with a Chinese filename, saved-script replay after full GUI process restart, target/decoy switching and guest resolution 1024×768 to 1280×1024 then restore.
- Confirmed missing MFC runtime prerequisite; fixed installation documentation and recorded the official signed artifact. No core code, test, tool or wheel-lock change.

## Evidence and recovery

Raw runs are ignored by Git and must never be erased or silently edited. [VALIDATION.md](VALIDATION.md) indexes accepted and failed attempts. [evidence/VALIDATION_SUMMARY.json](evidence/VALIDATION_SUMMARY.json) is a bounded summary, not replacement raw evidence.

The local acceptance directory `E:/final/desktrace-acceptance-20261016T151029Z/` contains full command argv/CWD/exit codes, numbered stdout/stderr, `summary.json`, a separate checkout and its own `runs/`. This source project's `runs/` retains earlier attempts and the system-app case.

The independent VM lab is `E:/final/desktrace-vm-build-20261017T013455Z/`. Read its `FINAL_RESULTS.json`, `REPORT.md`, `RESUME.md`, original archive hashes and failed attempts. Source validation used frozen commit `4ede97c5293c3d59378977d846ca76b9fd9bda81`; core tree `b233515b42ba2082b6f4a86792a861534aa825a8` is unchanged. Both owned guests are powered off; guest-only test startup was disabled and an acceptance snapshot retained. Guest credentials/media remain private and outside the source repo. Never rerun the VM provisioner against an existing disk as a way to resume.

Reproduce using [HANDOFF.md](HANDOFF.md), including the documented system runtime prerequisite on a clean Windows installation. Each command creates new output directories. No host security-setting changes, visible host desktop switching, untrusted app execution or other project changes are needed. A worker timeout means unknown target outcome: stop, inspect/reset the owned app and bind afresh. Never blindly retry input.

Recording writes its final script at save/EOF. On interruption, retain and manually reconstruct from per-operation evidence. Partial runs without final required files/manifest are incomplete. Do not manufacture missing evidence or change a failure to a pass.

## NOT RUN and next task

The original Windows 11 private-desktop Notepad probe remains a separate NOT RUN record. The independent Server guest's classic Notepad E2E and automated native GUI/file-picker/window-switch/resolution gates passed; see [docs/VM_ACCEPTANCE.md](docs/VM_ACCEPTANCE.md). Independent Windows 11 client installation, changed DPI, RDP/locked/service/cross-privilege operation, human usability, broad app coverage, deployment flakiness/error rates and comprehensive vulnerability/binary auditing remain NOT RUN.

Publication preparation now adds only README/support clarification, scope documents and SHA-pinned portable CI. Runtime, tests, tools, examples and locks remain unchanged from the owner-selected `b72487131337e86c6acf38ce385a202e2afc8cdb` baseline. See [source release boundary](docs/SOURCE_RELEASE.md). Exact candidate hashes and preparation logs are retained outside the public source tree. Hosted CI is NOT RUN until an authorized push.

The owner subsequently authorized source publication on 2026-10-17. Candidate `8f17d0106290fd21eaa5a4b6ad492efb84329e7f` was pushed to [KaiserIIII/desktrace](https://github.com/KaiserIIII/desktrace), with 58 remote blobs and KaiserIIII author/committer association verified. The first Linux hosted run failed its unittest command while mock CLI/evidence checks passed; the original workflow hid captured unittest stderr. A workflow-only diagnostic change exposes failed command logs without changing the test outcome. Read actual Actions and the external publication audit for the final CI verdict and any necessary fix; do not treat this initial failure as a PASS.

Feature development is stopped. A fresh Windows 11 client guest is useful before widening support, but no new feature work is scheduled. No installer, PyPI package or formal Release is published. Do not claim novelty or change the research NO-GO decision.
