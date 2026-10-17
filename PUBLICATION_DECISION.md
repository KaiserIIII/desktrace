# Publication decision

**LOCAL_HANDOFF_READY: YES, WITH LIMITATIONS.**

**PUBLICATION_READY: YES for a source-only experimental alpha within the tested scope.** This engineering decision follows the independent Windows desktop acceptance in [docs/VM_ACCEPTANCE.md](docs/VM_ACCEPTANCE.md) and a bounded local source/history/distribution review. It does not qualify a packaged installer or production release.

**PUBLIC_RELEASE_AUTHORIZED: NO.** No remote repository was created, and nothing was pushed, published or deployed. Publication still needs the owner's separate explicit instruction.

Delivered: modular Python UIA adapter, explicit recording, editable JSON, scoped replay and assertions, local failure screenshots/JSON/HTML/hashes, CLI, Tk GUI, mock adapter, regression tests, owned Windows fixture, real system-app demonstration, result comparison, repetition summary, bounded failure minimization, provenance/license/security/architecture/handoff documentation and checkpoints.

Actual evidence supports the original Windows 11 / Python 3.13 x64 development host and freshly provisioned Windows Server 2022 Desktop Experience / Python 3.13.0 x64 guests. Forty-one behavioral/CLI/boundary tests, all six native demonstration tools, installation, installed CLI, uninstall/import removal and reinstall passed independently. Classic Notepad, native recorder input, native Save/Open dialogs with a Chinese filename, recorder restart, explicit target/decoy switching and a 1024×768 to 1280×1024 resolution change passed. Repeated fixture runs and minimization remain controlled demonstrations, not deployment reliability estimates.

The clean VM exposed an undocumented MFC runtime prerequisite. Installing Microsoft's signed x64 runtime resolved the import failure; installation documentation and its provenance record were corrected. Product code, tests, tools and Python dependency versions were unchanged. Failed import and GUI test-driver attempts remain in the raw evidence. The frozen source used for validation is identified by commit/tree hashes in the VM record.

Independent Windows 11 client installation, changed DPI, RDP/locked/service/cross-privilege operation, human usability, broad app compatibility and comprehensive security/CVE auditing remain NOT RUN. A standalone installer and demo video are not delivered. There is no passive freeform recorder, arbitrary coordinate/key replay, general application reset/healing or measured deployment flake rate.

The release boundary is source, tests, owned fixture source, MIT license and reviewed documentation/sanitized summaries. Raw logs/screenshots, installers, vendor wheels, OS media, VM disks and guest-only credentials stay outside Git. Microsoft runtime binaries must be obtained from Microsoft; they are not redistributed. Original host/private-desktop Notepad limitations remain recorded separately.

Use a narrow experimental-alpha description and explicit privacy limits. Do not claim universal reliability, strong security isolation or scientific novelty. Existing research **NO-GO** conclusions are unchanged.
