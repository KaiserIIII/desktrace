# Critical engineering review

This is a local self-review by the implementing agent, not an independent human/security audit. No project code was uploaded to a third-party service. The available Codex Security plugin was not installed.

## Corrected reproducible defects

- P1 evidence usability: actual native capture was inverted and incorrectly sized at 200% DPI. The reproduction, old image and DPI probe were retained. Capture now matches the target thread DPI context and obtains an explicitly top-down DIB. New pixel-order tests and actual visual inspection cover the correction.
- P2 native execution: pywin32 did not expose the assumed process-image/window-maximized convenience APIs. Official kernel32 image query and supported window placement are used instead; the real fixture flow and placement regression test pass.
- P2 recording audit gap: failed explicit recordings originally had no bundle. CLI/GUI recordings now execute once through the same evidence pipeline, never append failed actions and never retry them. A regression test checks one execution and a valid failure bundle.
- P2 input contract: non-string action/state values leaked TypeError; strict type guards now produce contract errors before execution.
- P2 integrity checking: an empty manifest could pass the hash checker. Required evidence files are now mandatory; missing-file and tampering tests reject such bundles.
- P2 portability: Tcl resources existed but were undiscoverable from the Windows venv. A fallback uses only matching Tcl/Tk resources from the same Python base installation and preserves explicit settings. Both absent-resource and configured-resource tests pass.

## Deliberately retained limits

- P2 compatibility/acceptance: a fresh system-app E2E was not achieved on the private desktop. Physical GUI interaction/file pickers were not exercised. This blocks a claim of broad public readiness; the own-fixture alpha remains useful.
- P2 privacy boundary: text guard/password properties/window identity are trusted heuristics, not adversarial defenses. Screenshots remain opt-in and require manual review. Do not test personal apps.
- P2 recovery: provider timeout means the target action may already have happened. The tool stops, rather than blindly retries. Operators must reset/rebind. It does not restore app state automatically.
- P3 recorder ergonomics: explicit commands cover a deliberately small action vocabulary. No freeform passive recorder, coordinate/image fallback, drag/scroll/menu/toggle pattern coverage or general locator repair.
- P3 CLI persistence: script output is created at EOF after recording. If interrupted beforehand, per-operation evidence remains, but assembling those into the intended full script is manual.
- P3 minimization: signature-preserving greedy deletion is a bounded debugging aid and requires a safe reset callback. It may not find a global minimum and is not a proof of semantic equivalence.

No remaining known P0/P1 issue was observed in the tested owned-fixture scope. This statement does not establish safety for arbitrary apps, a production-ready status or a research contribution. Maintain the existing PatchVerdict research NO-GO decision; DeskTrace is a separate engineering project.

## Next decisive validation

Use a disposable Windows VM with a verified fresh system-app window. Complete input/read/restart/replay/failure/report there, then physically exercise GUI selection/record/save/load/replay without accessing private data. Evaluate whether a narrowly scoped public alpha is justified only after reviewing that evidence.
