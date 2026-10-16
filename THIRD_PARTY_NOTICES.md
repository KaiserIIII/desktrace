# Third-party materials

DeskTrace source, its WinForms fixture and examples are original project code under MIT. The Python/native dependencies keep their own licenses; they are not relicensed by this repository.

| Dependency | License metadata | Source and fixed commit |
| --- | --- | --- |
| pywinauto 0.6.9 | BSD-3-Clause | [source](https://github.com/pywinauto/pywinauto/tree/f6219c000d6d1bd676aec0486517afbac3ba9043) |
| comtypes 1.4.17 | MIT | [source](https://github.com/enthought/comtypes/tree/f855872f7da2e3ad561eca9861b488ecb8b6422f) |
| pywin32 312 | PSF metadata; inspect bundled component notices | [source](https://github.com/mhammond/pywin32/tree/2a277cb5552756c2b4d42b524dc36d25e0bb6354) |
| six 1.17.0 | MIT | [source](https://github.com/benjaminp/six/tree/ebd9b3af90247b8858d415a05e96e9ee61e48d07) |
| setuptools 84.0.0 (build tooling) | MIT metadata; bundled vendor licenses apply | [source](https://github.com/pypa/setuptools/tree/72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87) |

[DEPENDENCIES.json](DEPENDENCIES.json) records exact official wheel URLs/hashes and inspection time. Wheel metadata and bundled license files were examined locally; extracted copies remain in ignored `vendor/licenses/`. Python, Tcl/Tk, Windows, .NET Framework, and the system C# compiler are preexisting platform components, not distributed by DeskTrace. The compiler builds only our own fixture source; no downloaded upstream executable is run.

Git excludes wheels, reference-source/README snapshots, caches, local environments, compiled fixture executables and raw runs. Public source must not include another project's code or screenshots without a separate rights/privacy review. The upstream comparison uses links and bounded factual summaries. Nothing here licenses Microsoft installer binaries or third-party artwork for redistribution.

Installation operations: official artifact metadata inspected, fixed source commits resolved, SHA-256 verified against PyPI, then installed with `--no-index --require-hashes` in project-only virtual environments. No global package installation, recursive Skill install or external project clone was used for DeskTrace.
