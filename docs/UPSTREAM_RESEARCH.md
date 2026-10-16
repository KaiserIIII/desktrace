# Upstream engineering comparison

Inspected 2026-10-16 UTC through GitHub repository/commit/release APIs and actual README/source/license content. Metadata snapshots and downloaded reference source are retained locally under ignored `evidence/`; none was installed as a Skill. Context7 was attempted first but returned a monthly-quota limit; official sources were used instead. Commit timestamps are activity signals, not proof of active support or correctness.

| Project | License reported by GitHub | Fixed inspected HEAD | Latest release returned by API | Status/implication |
| --- | --- | --- | --- | --- |
| pywinauto | BSD-3-Clause | `47aa742389d3dbd3f1f5120c3fff7c601dfb0a06` (2026-10-15) | 0.6.9 (2025-01-06) | Not archived; recent source activity. Selected Python UIA backend. Installed release source is separately pinned below. |
| FlaUI | MIT | `fd7cc64ab01908a0ae4cc7d05e704caa34f98d16` (2026-08-13) | v5.0.0 (2025-02-25) | Not archived. Mature .NET alternative; not installed here. |
| Microsoft WinAppDriver | MIT source | `09e3f7111eb2fae2b4eff0ab058cc7a5dbc14d02` (2025-04-14) | v1.2.1 (2020-11-05) | Not archived, but upstream support warnings explicitly describe inactivity. Source license does not establish all installer/binary terms. |
| Appium Windows Driver | Apache-2.0 | `83193ee24bc20c7d819ad886ce4457c680cbc4dc` (2026-10-08) | v6.3.1 (2026-10-08) | Recent commits do not remove WinAppDriver dependency; current README says deprecated for Appium 4+. |
| pywinauto_recorder | MIT | `2ddc68645f30842c623f36f407083200589ce397` (2025-10-02) | 0.6.8 (2024-03-14) | Existing record/replay solution; inspected, not installed. |
| twenzel/FlaUIRecorder | MIT | `0d0ae02b3f98d6c8f567b2726e85a9bde3206704` (2020-09-21) | Not queried | README explicitly labels it abandoned. |
| FlaUI/FlaUIRec | MIT | `058375f6c2f6452da566337f2b5a9fd47b75bc0a` (2019-11-12) | Not queried | README contains only the project title; usable capability/support UNKNOWN. |

An initial `FlaUI/FlaUI.Recorder` lookup returned 404; GitHub repository search identified the actual repositories above. No capabilities were inferred from that nonexistent path.

## What already exists

[pywinauto's fixed source](https://github.com/pywinauto/pywinauto/tree/f6219c000d6d1bd676aec0486517afbac3ba9043) supplies window/control wrappers, descendant search and UIA interfaces. Its `uiawrapper.py`, `uia_element_info.py` and `uia_controls.py` were read from the exact 0.6.9 wheel, including Value/Text/Invoke access and default uncached descendant enumeration. DeskTrace calls these interfaces instead of implementing UIA COM discovery/protocol bindings. Compatibility still depends on the app's accessible controls and provider responsiveness.

[FlaUI's README](https://github.com/FlaUI/FlaUI/blob/fd7cc64ab01908a0ae4cc7d05e704caa34f98d16/README.md) exposes a .NET wrapper with UIA2/UIA3 choices and app launch/attach/window discovery. Its own description discusses framework-specific differences. It would suit a C# product, but adds another runtime to the requested Python MVP; no FlaUI execution was claimed.

[WinAppDriver](https://github.com/microsoft/WinAppDriver/blob/09e3f7111eb2fae2b4eff0ab058cc7a5dbc14d02/README.md) already provides a Selenium-style Windows automation service. Its setup requires installing a service and enabling Developer Mode. DeskTrace does neither. Installer terms and current binary compatibility were not independently tested.

[Appium Windows Driver's fixed README](https://github.com/appium/appium-windows-driver/blob/83193ee24bc20c7d819ad886ce4457c680cbc4dc/README.md) says it proxies WinAppDriver, warns about that server's maintenance, and identifies Appium WinCore Driver as its Appium 3/4-compatible replacement. This is more specific than the broad [Microsoft testing overview](https://learn.microsoft.com/en-us/windows/apps/develop/testing/) recommendation to use Appium Windows Driver. Resolve that documentation/version mismatch before adopting Appium. No Appium server, WinCore or alternative driver was installed or evaluated here.

[pywinauto_recorder's README](https://github.com/beuaaa/pywinauto_recorder/blob/2ddc68645f30842c623f36f407083200589ce397/README.rst) already describes recording actions into replayable Python. Its inspected [recorder implementation](https://github.com/beuaaa/pywinauto_recorder/blob/2ddc68645f30842c623f36f407083200589ce397/pywinauto_recorder/recorder.py) installs keyboard and mouse hooks. DeskTrace's explicit command recording deliberately avoids that mechanism; this is a scope/privacy choice, not a novelty claim or security judgment about the other project.

[twenzel/FlaUIRecorder](https://github.com/twenzel/FlaUIRecorder/blob/0d0ae02b3f98d6c8f567b2726e85a9bde3206704/README.md) describes a C# generator and lists verification improvements in its roadmap. Its abandonment badge is direct maintainer-provided evidence. [FlaUIRec](https://github.com/FlaUI/FlaUIRec/blob/058375f6c2f6452da566337f2b5a9fd47b75bc0a/README.md) was too sparsely documented to establish a usable feature set.

## Actual DeskTrace positioning

Window enumeration, UIA input, assertions, recording, replay, screenshots and reports are established engineering capabilities. DeskTrace's value proposition is a small inspectable Python workflow: one explicit window binding, editable data-only scripts, bounded worker waiting, and local evidence with clearly labeled simulations. No superiority, first discovery, scientific innovation or generalization claim is supported by these comparisons.

## OS APIs checked against official documentation

- [QueryFullProcessImageNameW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew): limited-query process identity.
- [CreateDesktopW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createdesktopw): separate owned test desktop; no SwitchDesktop call.
- [Value.SetValue requirements](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomationvaluepattern-setvalue): enabled and not read-only.
- [PrintWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-printwindow): selected-window rendering; provider-dependent and potentially blocking.
- [DPI APIs](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-reference): thread DPI context matching for capture. Runtime probes confirmed the 2× size mismatch before the correction.
