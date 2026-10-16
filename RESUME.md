# DeskTrace resume checkpoint

## Current state

Engineering implementation and local acceptance are complete. Keep this project local; no public remote, push, release or deployment is authorized. Existing scientific NO-GO conclusions remain unchanged. Read [PUBLICATION_DECISION.md](PUBLICATION_DECISION.md) before any scope change.

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

## Evidence and recovery

Raw runs are ignored by Git and must never be erased or silently edited. [VALIDATION.md](VALIDATION.md) indexes accepted and failed attempts. [evidence/VALIDATION_SUMMARY.json](evidence/VALIDATION_SUMMARY.json) is a bounded summary, not replacement raw evidence.

The local acceptance directory `E:/final/desktrace-acceptance-20261016T151029Z/` contains full command argv/CWD/exit codes, numbered stdout/stderr, `summary.json`, a separate checkout and its own `runs/`. This source project's `runs/` retains earlier attempts and the system-app case.

Reproduce using [HANDOFF.md](HANDOFF.md). Each command creates new output directories. No global installation/security changes, visible desktop switching, untrusted app execution or other project changes are needed. A worker timeout means unknown target outcome: stop, inspect/reset the owned app and bind afresh. Never blindly retry input.

Recording writes its final script at save/EOF. On interruption, retain and manually reconstruct from per-operation evidence. Partial runs without final required files/manifest are incomplete. Do not manufacture missing evidence or change a failure to a pass.

## NOT RUN and next task

Notepad E2E remains NOT RUN: no unique owned window appeared in its bounded probe. Physical-input GUI/file-picker acceptance, a second Windows host/VM, broad app coverage, deployment flakiness/error rates and comprehensive vulnerability/binary audit remain NOT RUN.

Next: disposable Windows VM acceptance with physical GUI select/record/save/load/replay/failure and an independent system-app repeat. Public release needs separate explicit authorization and a fresh source/history/privacy audit. Do not expand functionality or claim novelty to compensate for missing validation.
