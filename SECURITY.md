# Safety, privacy and release boundary

DeskTrace is for **authorized, non-sensitive desktop test applications**. It is not a sandbox, antivirus, secret scanner, password recorder or unattended operator for an unrestricted workstation. Use a disposable Windows test account/VM for broader validation.

## Implemented controls

- No system-wide keyboard/mouse listener, clipboard reader, remote API, telemetry, shell/script operation, coordinate input or global screen capture.
- Native CLI actions require an explicit HWND/PID and `--authorize`. GUI operations require selecting/binding a target and the authorization checkbox. Authorization is an assertion by the operator, not an OS security capability.
- The runtime freezes HWND/PID/process creation time/window class; searches only the selected UIA subtree and filters to the same PID. Unknown/reused/missing identities and ambiguous locators stop execution. Known terminal, lock, authentication, password-manager and security executable names are denied. This denylist is incomplete and is not an adversarial security boundary.
- Password state is checked before reading selected-control text. An unknown password property fails closed; inspection omits password controls. A password anywhere in the scoped target suppresses its screenshot. Providers can lie or omit privacy properties.
- Conservative input guards reject obvious secret assignments/token forms/email addresses. Ordinary names, phone numbers, arbitrary secrets, custom password fields and secrets embedded in permitted text can escape detection. The caller must supply only public test data.
- Logs/results store observed text as hashes/lengths and redact provider exception bodies. Scripts preserve input/expected text in plain JSON. Hashes are not encryption; screenshots, AutomationIds, window classes and absolute output paths can reveal private data.
- Screenshots are opt-in, target-only, bounded-size PrintWindow captures with no whole-screen fallback. A changing control tree can race the password scan. Opt-in does not guarantee privacy; review before sharing.
- Workers have deadlines and no automatic retry after an unknown input outcome. Killing the worker does not undo actions already sent to the app or guarantee a hung provider returns. Failed/partial runs remain for diagnosis.
- Escaped static HTML uses a restrictive CSP and no remote resources. Run directories are new UUID paths. Manifest verification detects mismatches relative to a trusted manifest; it does not authenticate execution.

## Trusted components and residual risks

Trust Windows, same-privilege app UIA providers, the user's window/data authorization and local filesystem. Local input scripts/locks/manifests can be edited by the local user. The product does not defend against malicious scripts that invoke destructive controls in a selected application. It does not reliably recognize all sensitive apps. UIA/provider bugs, handle/control races, app child processes, UAC/elevation, locked/RDP/service sessions, DPI/multiple monitors and GPU rendering remain risks.

The non-visible desktop in demo tools is only a way to separate our owned UI from the user's current desktop. It shares the Windows account, filesystem, network and OS. No untrusted application is safe merely because it runs there. Demo cleanup terminates only its own held process handles, after retaining evidence; the main CLI/GUI never terminates a user's selected process.

## Audit performed in this delivery

Manual local source review, strict-input tests, password/ambiguity tests (mock and actual owned controls), timeout-boundary tests, hash/HTML tests and tracked-file secret/privacy review. The Codex Security plugin is not installed; no claim of its scan or an independent professional security assessment is made. Dependencies were origin/version/hash/license checked; no comprehensive vulnerability database or binary audit was run. No private project code was uploaded to a third-party review service.

## Before any public publication

Keep `.venv*`, `vendor/`, `runs/` and raw `evidence/` out of Git. Review the exact tracked list and full history for secrets/private paths. Only deliberately sanitized summaries belong in version control. No raw user-window inventory, original research project data, local identity backups, credentials, personal screenshots or third-party binaries should be published. `.gitignore` is a convenience, not proof of clearance.

DeskTrace currently has no remote and no release. The independent Server 2022 desktop gates passed within the scope in [VM_ACCEPTANCE.md](docs/VM_ACCEPTANCE.md); source-only experimental-alpha preparation is complete. Publication still requires separate owner authorization. Independent Windows 11, DPI and RDP validation remain NOT RUN. Do not market it as generally secure or fully validated.
